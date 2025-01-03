import "./LoginForm.css";

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const LoginForm: React.FC = () => {
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string>('');
    const navigate = useNavigate();

    /**
     * handleSubmit - Обработчик отправки формы для входа пользователя.
     * 
     * Эта асинхронная функция выполняется при отправке формы входа. Она предотвращает 
     * стандартное поведение формы, отправляет POST-запрос на сервер для аутентификации 
     * пользователя и обрабатывает ответ. 
     * 
     * Основные шаги:
     * 1. Предотвращает стандартное поведение формы с помощью e.preventDefault().
     * 2. Отправляет POST-запрос на '/api/login' с данными пользователя (имя пользователя и пароль).
     * 3. Если ответ от сервера не успешен (response.ok == false), выбрасывает ошибку с сообщением 
     *    'Некорректный логин или пароль'.
     * 4. Если аутентификация успешна, извлекает роль пользователя из ответа сервера:
     *    - Если роль 'admin', перенаправляет на административную панель ('/admin-panel').
     *    - Если роль обычного пользователя, перенаправляет на панель файлового хранилища ('/file-storage').
     * 5. Обрабатывает любые ошибки, которые могут возникнуть во время запроса:
     *    - Устанавливает сообщение об ошибке с помощью setError().
    */
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        try {
            const response = await fetch('/api/login', {  // WIP: сервер еще не готов
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                throw new Error('Некорректный логин или пароль');
            }

            const data = await response.json();

            const { role } = data; // !!! Cервер должен возвращать объект пользователя с полем role
            
            if (role === 'admin') {
                navigate('/admin-panel');  // WIP: административная панель еще в разработке
            } else {
                navigate('/file-storage');  // WIP: панель для обычных пользователей еще в разработке
            }
        } catch (err: unknown) {
            console.error(err);
            if (err instanceof Error) {
                setError(err.message); // Устанавливаем сообщение об ошибке
            } else {
                setError('Произошла ошибка'); // Ответ, если это не ошибка
            }
        }
    };

    return (
        <div className="wrap">
            <h2>Введите данные для входа</h2>
            <form onSubmit={handleSubmit}>
                <div className="input-signin">
                    <label>
                        Логин:
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </label>
                </div>
                <div className="input-signin">
                    <label>
                        Пароль:
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </label>
                </div>
                {error && <div style={{ color: 'red' }}>{error}</div>}
                <button className="button-signin" type="submit">Войти</button>
            </form>
        </div>
    );
};
