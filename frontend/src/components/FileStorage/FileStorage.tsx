import { useEffect, useState } from 'react';
import './FileStorage.css';

interface FileItem {
    id: number;
    name: string;
    comment: string;
    size: number;
    uploadDate: string;
    lastDownloadDate: string;
}

export const FileStorage: React.FC = () => {
    const [files, setFiles] = useState<FileItem[]>([]);  // Состояние для хранения списка файлов
    const [error, setError] = useState<string>('');  // Cостояние для хранения сообщения об ошибках
    const [selectedFile, setSelectedFile] = useState<File | null>(null);  // Состояние для хранения выбранного файла для загрузки
    const [comment, setComment] = useState<string>('');  // Состояние для хранения комментария к загружаемому файлу
    const [isLoading, setIsLoading] = useState<boolean>(false);  // Состояние для отслеживания состояния загрузки

    /**
     * Эффект, который загружает файлы из API при монтировании компонента.
     */
    useEffect(() => {
        const fetchFiles = async () => {
            setIsLoading(true);
            try {
                const response = await fetch('http://localhost:5000/api/storage');
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
            }
        };
        fetchFiles();
    }, []);

    /**
     * Обработчик загрузки файла. Загружает выбранный файл и комментарий на сервер.
     * 
     * При отправке формы функция проверяет наличие выбранного файла. Если файл выбран, 
     * он добавляется в объект FormData вместе с комментарием. Затем функция отправляет
     * POST-запрос на сервер для загрузки файла. В случае успешной загрузки обновляется
     * список файлов и сбрасываются выбранный файл и комментарий. 
     * Также обрабатываются ошибки, которые могут возникнуть во время загрузки.
     * 
     * @param {React.FormEvent<HTMLFormElement>} e - Событие отправки формы.
     */
    const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!selectedFile) return; // Если файл не выбран, прерываем выполнение функции
        
        // Создаем новый объект FormData и добавляем в него выбранный файл и комментарий
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('comment', comment);

        setIsLoading(true); // Устанавливаем состояние загрузки в true
        try {
            // Выполняем POST-запрос на сервер для загрузки файла
            const response = await fetch('http://localhost:5000/api/storage/upload', {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) {
                throw new Error('Не удалось загрузить файл'); // Обработка неуспешного ответа
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
            setIsLoading(false); // В любом случае устанавливаем состояние загрузки в false
        }
    };

    /**
     * Обработчик удаления файла. Удаляет файл с указанным идентификатором.
     * 
     * Функция отправляет DELETE-запрос на сервер для удаления файла с заданным 
     * идентификатором. Если делается успешный запрос, файл удаляется из состояния 
     * компонента. В случае возникновения ошибки при удалении, она обрабатывается 
     * и выводится сообщение об ошибке.
     * 
     * @param {number} fileId - Идентификатор файла, который нужно удалить.
     */
    const handleDelete = async (fileId: number) => {
        setIsLoading(true); // Устанавливаем состояние загрузки в true
        try {
            // Выполняем DELETE-запрос на сервер для удаления файла с указанным идентификатором
            const response = await fetch(`http://localhost:5000/api/storage/delete/${fileId}`, {
                method: 'DELETE',
            });
            
            if (!response.ok) {                
                throw new Error('Не удалось удалить файл'); // Обработка неуспешного ответа
            }

            // Обновляем состояние файлов, исключая удаляемый файл
            const newFiles = files.filter(file => file.id !== fileId);
            setFiles(newFiles); // Устанавливаем новое состояние файлов
        } catch (err: unknown) {
            console.error(err); // Логируем ошибку
            if (err instanceof Error) {
                setError(err.message); // Устанавливаем сообщение об ошибке для отображения
            } else {
                setError('Произошла ошибка при удалении файла'); // Сообщение по умолчанию
            }
        } finally {
            setIsLoading(false); // В любом случае устанавливаем состояние загрузки в false
        }
    };

    /**
     * Обработчик переименования файла. Переименовывает файл с указанным идентификатором.
     * 
     * Функция отправляет POST-запрос на сервер для изменения имени файла с заданным
     * идентификатором. Если запрос успешен, состояние файла обновляется, и новое имя 
     * устанавливается как текущее для файла. В случае ошибки во время процесса переименования,
     * функция обрабатывает её и выводит сообщение об ошибке.
     * 
     * @param {number} fileId - Идентификатор файла, который нужно переименовать.
     * @param {string} newName - Новое имя для файла.
     */
    const handleRename = async (fileId: number, newName: string) => {
        setIsLoading(true); // Устанавливаем состояние загрузки в true
        try {
            // Выполняем POST-запрос на сервер для переименования файла
            const response = await fetch(`http://localhost:5000/api/storage/rename/${fileId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: newName }), // Отправляем новое имя файла в теле запроса
            });
            if (!response.ok) {
                throw new Error('Не удалось переименовать файл'); // Обработка неуспешного ответа
            }
            const updatedFile = await response.json(); // Получаем обновленные данные файла

            // Обновляем состояние файлов, заменяя старое имя на новое
            setFiles(files.map(file => (file.id === fileId ? updatedFile : file)));
        } catch (err: unknown) {
            console.error(err); // Логируем ошибку
            if (err instanceof Error) {
                setError(err.message); // Устанавливаем сообщение об ошибке для отображения
            } else {
                setError('Произошла ошибка при переименовании файла'); // Сообщение по умолчанию
            }
        } finally {
            setIsLoading(false); // В любом случае устанавливаем состояние загрузки в false
        }
    };

    /**
     * Обработчик копирования ссылки на файл. Копирует URL файла с указанным идентификатором в буфер обмена.
     * 
     * Функция создает ссылку на файл, используя его идентификатор, и затем записывает
     * эту ссылку в буфер обмена с помощью API clipboard. В случае успешного копирования
     * выводится сообщение об успешном завершении. Если возникает ошибка во время копирования,
     * ошибка логируется в консоль.
     * 
     * @param {number} fileId - Идентификатор файла, для которого нужно скопировать ссылку.
     */
    const handleCopyLink = (fileId: number) => {
        // Формируем ссылку на файл, используя его идентификатор
        const fileLink = `http://localhost:5000/api/storage/file/${fileId}`;
        // Копируем ссылку в буфер обмена
        navigator.clipboard.writeText(fileLink)
            .then(() => alert('Ссылка скопирована!')) // Сообщение об успешном копировании
            .catch(err => console.error('Ошибка при копировании ссылки:', err)); // Логируем ошибку
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
                            <tr key={file.id}>
                                <td>{file.name}</td>
                                <td>{file.comment}</td>
                                <td>{file.size}</td>
                                <td>{new Date(file.uploadDate).toLocaleString()}</td>
                                <td>{new Date(file.lastDownloadDate).toLocaleString()}</td>
                                <td>
                                    <button onClick={() => handleDelete(file.id)}>Удалить</button>
                                    <button onClick={() => {
                                        const newName = prompt('Введите новое имя файла:', file.name);
                                        if (newName) handleRename(file.id, newName);
                                    }}>Переименовать</button>
                                    <button onClick={() => handleCopyLink(file.id)}>Копировать ссылку</button>
                                    <a href={`http://localhost:5000/api/storage/file/${file.id}`} target="_blank" rel="noopener noreferrer">Просмотр</a>
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
