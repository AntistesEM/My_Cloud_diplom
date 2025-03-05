import "./LoginForm.css";

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const LoginForm: React.FC<{ updateAuth: (authStatus: boolean, role: string) => void }> = ({ updateAuth }) => {
    const [username, setUsername] = useState<string>('');  // Состояние для хранения имени пользователя, вводимого в форму
    const [password, setPassword] = useState<string>('');  // Состояние для хранения пароля, вводимого в форму
    const [error, setError] = useState<string>('');  // Состояние для хранения сообщения об ошибке в случае неудачной аутентификации
    const navigate = useNavigate();  // Хук для навигации между страницами приложения в зависимости от роли пользователя

    /**
     * handleSubmit - Обработчик отправки формы для входа пользователя.
     * 
     * Эта асинхронная функция выполняется при отправке формы входа. Она предотвращает 
     * стандартное поведение формы, что может привести к перезагрузке страницы, 
     * отправляет POST-запрос на сервер для аутентификации пользователя и обрабатывает ответ. 
     * 
     * Основные шаги:
     * 1. Предотвращает стандартное поведение формы с помощью e.preventDefault().
     * 2. Отправляет POST-запрос на '/api/login' с данными пользователя (имя пользователя и пароль).
     * 3. Если ответ от сервера не успешен (response.ok === false), выбрасывает ошибку с сообщением 
     *    'Некорректный логин или пароль'.
     * 4. Если аутентификация успешна, извлекает токен и роль пользователя из ответа сервера:
     *    - Если роль 'admin', перенаправляет на административную панель ('/admin').
     *    - Если роль 'user', перенаправляет на панель файлового хранилища ('/storage/{userId}').
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
            const response = await fetch('http://localhost:5000/api/login', {
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

            const { id, token, role } = data; // Достаем id, токен и роль

            // Сохранение токена и роли в localStorage
            localStorage.setItem('token', token);
            localStorage.setItem('role', role);
            
            // Обновляем аутентификацию
            updateAuth(true, role); 
            
            // Переход на соответствующую страницу в зависимости от роли
            if (role === 'admin') {
                navigate('/admin');
            } else {
                navigate(`/storage/${id}`);
            }
        } catch (err: unknown) {
            console.error(err);
            if (err instanceof Error) {
                setError(err.message); // Устанавливаем сообщение об ошибке
            } else {
                setError('Произошла ошибка'); // Сообщение по умолчанию, если это не ошибка
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
