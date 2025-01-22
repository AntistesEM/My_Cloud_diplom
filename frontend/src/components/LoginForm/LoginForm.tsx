import "./LoginForm.css";

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const LoginForm: React.FC = () => {
    const [username, setUsername] = useState<string>('');  // Состояние для хранения имени пользователя, вводимого в форму
    const [password, setPassword] = useState<string>('');  // Состояние для хранения пароля, вводимого в форму
    const [error, setError] = useState<string>('');  // Состояние для хранения сообщения об ошибке в случае неудачной аутентификации
    const navigate = useNavigate();  // Хук для навигации между страницами приложения в зависимости от роли пользователя

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
     * 4. Если аутентификация успешна, извлекает токен и роль пользователя из ответа сервера:
     *    - Если роль 'admin', перенаправляет на административную панель ('/adminpanel').
     *    - Если роль обычного пользователя, перенаправляет на панель файлового хранилища ('/storage').
     * 5. Обрабатывает любые ошибки, которые могут возникнуть во время запроса:
     *    - Устанавливает сообщение об ошибке с помощью setError().
     * 
     * Ожидаемые данные от сервера: 
     * - Токен аутентификации (token)
     * - Роль пользователя (role) (значения могут быть 'admin' или 'user')
     */
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        try {
            const response = await fetch('http://localhost:5000/api/login', {  // WIP: сервер еще не готов
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

            const { token, role } = data; // Достаем токен и роль

            // Сохранение токена и роли в localStorage
            localStorage.setItem('token', token);
            localStorage.setItem('role', role); 
            
            // Переход на соответствующую страницу в зависимости от роли
            if (role === 'admin') {
                navigate('/adminpanel');  // WIP: административная панель еще в разработке
            } else {
                navigate('/storage');  // WIP: панель для обычных пользователей еще в разработке
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
