import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import './FileStorage.css';

interface FileItem {
    id_file: number;
    original_name: string;
    comment: string;
    size: number;
    upload_date: string;
    last_download_date: string;
}

export const FileStorage: React.FC = () => {
    const { id_user } = useParams<{ id_user: string }>(); // Получаем ID пользователя из URL
    const [files, setFiles] = useState<FileItem[]>([]);  // Состояние для хранения списка файлов
    const [error, setError] = useState<string>('');  // Cостояние для хранения сообщения об ошибках
    const [selectedFile, setSelectedFile] = useState<File | null>(null);  // Состояние для хранения выбранного файла для загрузки
    const [comment, setComment] = useState<string>('');  // Состояние для хранения комментария к загружаемому файлу
    const [isLoading, setIsLoading] = useState<boolean>(false);  // Состояние для отслеживания состояния загрузки
    
    /**
     * Хук, который загружает файлы из API при монтировании компонента.
     */
    useEffect(() => {
        const fetchFiles = async () => {
            setIsLoading(true);
            try {
                const response = await fetch(`http://localhost:8000/api/storage/${id_user}`);
                if (!response.ok) {
                    throw new Error('Не удалось загрузить файлы');
                }
                const data = await response.json();
                setFiles(data);
            } catch (err: unknown) {
                console.error(err);
                if (err instanceof Error) {
                    setError(err.message);
                } else {
                    setError('Произошла ошибка при загрузке файлов');
                }
            } finally {
                setIsLoading(false);
                setTimeout(() => {
                    setError('');
                }, 3000);
            }
        };
        fetchFiles();
    }, [id_user]);
    
    /**
     * Обработчик загрузки файла. Загружает выбранный файл и комментарий на сервер.
     * 
     * При отправке формы функция проверяет наличие выбранного файла. Если файл выбран, 
     * он добавляется в объект FormData вместе с комментарием. Затем функция отправляет
     * POST-запрос на сервер для загрузки файла. При успешной загрузке обновляется
     * список файлов, и происходит сброс выбранного файла и комментария. 
     * Также обрабатываются ошибки, которые могут возникнуть во время загрузки.
     *
     * Функция также устанавливает состояние загрузки в true до завершения запроса 
     * и устанавливает его в false в любом случае, чтобы 
     * отразить состояние загрузки в пользовательском интерфейсе.
     * 
     * @param {React.FormEvent<HTMLFormElement>} e - Событие отправки формы.
     */
    const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        // Если файл не выбран, прерываем выполнение функции
        if (!selectedFile) return;
        
        // Создаем новый объект FormData и добавляем в него выбранный файл и комментарий
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('comment', comment);

        setIsLoading(true); // Устанавливаем состояние загрузки в true
        try {
            const response = await fetch(`http://localhost:8000/api/storage/${id_user}/`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) {
                throw new Error('Не удалось загрузить файл');
            }
            const newFiles = await response.json(); // Получаем новый список файлов после загрузки
            setFiles(newFiles); // Обновляем состояние файлов
            setComment(''); // Сбрасываем поле комментария
            setSelectedFile(null); // Сбрасываем выбранный файл
        } catch (err: unknown) {
            console.error(err); // Логируем ошибку
            if (err instanceof Error) {
                setError(err.message); // Устанавливаем сообщение об ошибке для отображения
            } else {
                setError('Произошла ошибка при загрузке файла'); // Сообщение по умолчанию
            }
        } finally {
            setIsLoading(false);
            setTimeout(() => {
                setError('');
            }, 3000);
        }
    };

    /**
     * Обработчик удаления файла. Удаляет файл с указанным идентификатором.
     * 
     * Функция отправляет DELETE-запрос на сервер для удаления файла с заданным 
     * идентификатором. Если запрос завершен успешно, файл удаляется из состояния, 
     * хранящего список файлов, в компоненте. В случае возникновения ошибки при 
     * удалении, ошибка обрабатывается и выводится сообщение об ошибке пользователю.
     * 
     * @param {number} id_file - Идентификатор файла, который нужно удалить.
     */
    const handleDelete = async (id_file: number) => {
        setIsLoading(true); // Устанавливаем состояние загрузки в true
        try {
            const response = await fetch(`http://localhost:8000/api/storage/${id_user}/${id_file}/`, {
                method: 'DELETE',
            });
            
            if (!response.ok) {
                throw new Error('Не удалось удалить файл');
            }

            // Обновляем состояние файлов, исключая удаляемый файл
            const newFiles = files.filter(file => file.id_file !== id_file);

            setFiles(newFiles); // Устанавливаем новое состояние файлов
        } catch (err: unknown) {
            console.error(err); // Логируем ошибку
            if (err instanceof Error) {
                setError(err.message); // Устанавливаем сообщение об ошибке для отображения пользователю
            } else {
                setError('Произошла ошибка при удалении файла'); // Сообщение по умолчанию
            }
        } finally {
            setIsLoading(false);
            setTimeout(() => {
                setError('');
            }, 3000);
        }
    };

    /**
     * Обработчик переименования файла. Переименовывает файл с указанным идентификатором.
     * 
     * Функция отправляет POST-запрос на сервер для изменения имени файла с заданным
     * идентификатором. Если запрос завершен успешно, состояние файла обновляется, 
     * и новое имя устанавливается как текущее имя для переименованного файла. 
     * В случае возникновения ошибки во время процесса переименования, 
     * функция обрабатывает её и выводит сообщение об ошибке пользователю.
     * 
     * @param {number} id_file - Идентификатор файла, который нужно переименовать.
     * @param {string} newName - Новое имя для файла.
     */
    const handleRename = async (id_file: number, newName: string) => {
        setIsLoading(true); // Устанавливаем состояние загрузки в true
        try {
            const response = await fetch(`http://localhost:8000/api/storage/${id_user}/${id_file}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: newName }), // Отправляем новое имя файла в теле запроса
            });// Проверяем статус ответа

            if (!response.ok) {
                const errorData = await response.json(); // Получаем данные об ошибке
                if (response.status === 400 && errorData) {
                    throw new Error(JSON.stringify(errorData)); // Генерируем ошибку с сообщением из ответа
                } else {
                    throw new Error('Не удалось переименовать файл');
                }
            }
            
            const updatedFile = await response.json(); // Получаем обновленные данные файла

            // Обновляем состояние файлов, заменяя старое имя на новое для конкретного файла
            setFiles(files.map(file => (file.id_file === id_file ? updatedFile : file)));
        } catch (err: unknown) {
            console.error(err); // Логируем ошибку
            if (err instanceof Error) {
                setError(err.message); // Устанавливаем сообщение об ошибке для отображения пользователю
            } else {
                setError('Произошла ошибка при переименовании файла'); // Сообщение по умолчанию
            }
        } finally {
            setIsLoading(false);
            setTimeout(() => {
                setError('');
            }, 3000);
        }
    };

    const handleDownload = (id_file: number) => {
        setIsLoading(true); // Устанавливаем состояние загрузки в true
        try {
            // Переход к URL для скачивания файла
            window.location.href = `http://localhost:8000/api/storage/download/${id_file}/`;
        } catch (err) {
            console.error(err); // Логируем ошибку
            setError('Произошла ошибка при скачивании файла'); // Сообщение по умолчанию
        } finally {
            setIsLoading(false); // Установка состояния загрузки в false
        }
    };
    

    
    // const handleDownload = async (id_file: number) => {
    //     try {
    //         const response = await fetch(`http://localhost:8000/api/storage/${id_user}/${id_file}/download`, {
    //             method: 'GET',
    //         });

    //         if (!response.ok) {
    //             throw new Error('Не удалось загрузить файл');
    //         }

    //         const blob = await response.blob();
    //         const url = window.URL.createObjectURL(blob);
    //         const link = document.createElement('a');
    //         link.href = url;
    //         link.download = files.find(file => file.id_file === id_file)?.name || '';
    //         link.click();
    //     } catch (err: unknown) {
    //         console.error(err); // Логируем ошибку
    //         if (err instanceof Error) {
    //             setError(err.message); // Устанавливаем сообщение об ошибке для отображения пользователю
    //         } else {
    //             setError('Произошла ошибка при загрузке файла'); // Сообщение по умолчанию
    //         }
    //     } finally {
    //         setIsLoading(false);
    //         setTimeout(() => {
    //             setError('');
    //         }, 3000);
    //     }

    // /**
    //  * Обработчик копирования ссылки на файл. Копирует URL файла с указанным идентификатором в буфер обмена.
    //  * 
    //  * Функция формирует ссылку на файл, используя его идентификатор и идентификатор пользователя, 
    //  * и затем записывает эту ссылку в буфер обмена с помощью API clipboard. 
    //  * В случае успешного копирования выводится сообщение об успешном завершении. 
    //  * Если возникает ошибка во время копирования, она логируется в консоль.
    //  * 
    //  * @param {string | undefined} userId - Идентификатор пользователя, связанный с файлом.
    //  * @param {number} fileId - Идентификатор файла, для которого нужно скопировать ссылку.
    //  */
    // const handleCopyLink = (userId: string | undefined, fileId: number) => {
    //     // Формируем ссылку на файл, используя идентификатор пользователя и файл
    //     const fileLink = `http://localhost:5000/api/storage/file/${userId}/${fileId}`;
    //     // Копируем ссылку в буфер обмена
    //     navigator.clipboard.writeText(fileLink)
    //         .then(() => alert('Ссылка скопирована!')) // Сообщение об успешном копировании
    //         .catch(err => console.error('Ошибка при копировании ссылки:', err)); // Логируем ошибку
    // };
    
    const handleLink = async (id_file: number) => {
        setIsLoading(true); // Устанавливаем состояние загрузки в true
        try {
            const response = await fetch(`http://localhost:8000/api/storage/link/${id_user}/${id_file}/`, {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token'), 
                    'Content-Type': 'application/json'
                }
            });
    
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
    
            const data = await response.json();
            console.log("Ссылка на файл: ", data.file_link);
            alert("Ссылка на файл: " + data.file_link);
        } catch (error) {
            console.error("Ошибка получения ссылки:", error);
        } finally {
            setIsLoading(false);
            setTimeout(() => {
                setError('');
            }, 3000);
        }
    };

        return (
            <div className="wrap">
                <h2>Файлы</h2>
                {isLoading && <div>Загрузка...</div>}
                {error && <div style={{ color: 'red' }}>{error}</div>}
                <form className="form-storage" onSubmit={handleUpload}>
                    <input className="input-storage"
                        type="file"
                        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    />
                    <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Комментарий для файла"
                        required
                    />
                    <button type="submit">Загрузить</button>
                </form>
                {files.length > 0 ? (
                    <table>
                        <thead>
                            <tr>
                                <th>Имя файла</th>
                                <th>Комментарий</th>
                                <th>Размер (байт)</th>
                                <th>Дата загрузки</th>
                                <th>Дата последнего скачивания</th>
                                <th>Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            {files.map(file => (
                                <tr key={file.id_file}>
                                    <td>{file.original_name}</td>
                                    <td>{file.comment}</td>
                                    <td>{file.size}</td>
                                    <td>{new Date(file.upload_date).toLocaleString()}</td>
                                    <td>
                                        {file.last_download_date ? new Date(file.last_download_date).toLocaleString() : 'Нет данных'}
                                    </td>
                                    {/* <td>{new Date(file.last_download_date).toLocaleString()}</td> */}
                                    <td>
                                        <button onClick={() => handleDelete(file.id_file)}>Удалить</button>
                                        <button onClick={() => {
                                            const newName = prompt('Введите новое имя файла:');
                                            if (newName && newName.trim()) {
                                                handleRename(file.id_file, newName);
                                            } else {
                                                alert('Имя файла не может быть пустым.');
                                            }
                                        }}>
                                            Переименовать
                                        </button>
                                        <button onClick={() => handleDownload(file.id_file)} >Скачать</button>
                                        <button onClick={() => handleLink(file.id_file)}>Копировать ссылку</button>
                                        <a href={`http://localhost:8000/api/storage/view/${id_user}/${file.id_file}/`} target="_blank" rel="noopener noreferrer">Просмотр</a>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>Нет загруженных файлов.</p>
                )}
            </div>
    );
};
