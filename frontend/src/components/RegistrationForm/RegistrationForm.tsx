import "./RegistrationForm.css";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const RegistrationForm: React.FC = () => {
    const [username, setUsername] = useState<string>('');
    const [fullName, setFullName] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string>('');  // Сообщение об ошибке
    const [success, setSuccess] = useState<string>('');  // Сообщение об успехе
    const navigate = useNavigate();

    /**
     * Проверяет корректность введенных данных формы.
     * 
     * @returns {boolean} Возвращает true, если все поля валидны, иначе false.
    */
    const validateForm = (): boolean => {
        // Проверка логина: только латинские буквы и цифры, первый символ – буква, длина от 4 до 20 символов
        const usernameRegex = /^[a-zA-Z][a-zA-Z0-9]{3,19}$/;
        if (!usernameRegex.test(username)) {
            setError('Логин должен начинаться с буквы, содержать только латинские буквы и цифры, и быть длиной от 4 до 20 символов.');
            return false;
        }

        // Проверка email
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(email)) {
            setError('Неверный формат email.');
            return false;
        }

        // Проверка пароля: не менее 6 символов, хотя бы одна заглавная буква, одна цифра и один специальный символ
        const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$/;
        if (!passwordRegex.test(password)) {
            setError('Пароль должен содержать минимум 6 символов, одну заглавную букву, одну цифру и один специальный символ.');
            return false;
        }

        setError(''); // Сбрасываем ошибки, если все проверки пройдены
        return true;
    };

    /**
     * Обрабатывает отправку формы регистрации.
     * 
     * @param {React.FormEvent<HTMLFormElement>} e - Событие отправки формы.
     * @returns {void}
     * 
     * Функция предотвращает стандартное поведение формы, проверяет валидность данных с помощью
     * функции validateForm, и если данные валидны, отправляет запрос на сервер для
     * регистрации пользователя. В случае успеха отображает сообщение об успешной регистрации
     * и перенаправляет пользователя на страницу входа. В случае ошибки отображает сообщение об ошибке.
    */
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (!validateForm()) {
            return; // Прерываем выполнение, если проверка не пройдена
        }

        try {
            const response = await fetch('/api/register', {  // WIP: сервер еще не готов
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, fullName, email, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Ошибка во время регистрации');
            }

            setSuccess('Регистрация прошла успешно!'); // Успешное сообщение
            setTimeout(() => {
                navigate('/signin'); // Перенаправляем на страницу "Вход"
            }, 2000);
        } catch (err: unknown) {
            console.error(err);
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError('Произошла ошибка');
            }
        }
    };

    return (
        <div className="wrap">
            <h2>Введите данные для регистрации</h2>
            <form onSubmit={handleSubmit}>
                <div className="input-signup">
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
                <div className="input-signup">
                    <label>
                        Полное имя:
                        <input
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            required
                        />
                    </label>
                </div>
                <div className="input-signup">
                    <label>
                        Email:
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </label>
                </div>
                <div className="input-signup">
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
                {error && <div className="error-message">{error}</div>}
                {success && <div className="success-message">{success}</div>}
                <button className="button-signup" type="submit">Зарегистрироваться</button>
            </form>
        </div>
    );
};
