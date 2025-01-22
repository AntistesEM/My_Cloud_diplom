import { Link, useLocation } from "react-router-dom";

/**
 * Navbar - компонент навигационной панели.
 *
 * Компонент отображает навигационные ссылки на разные страницы приложения.
 * В зависимости от текущего пути (location.pathname), ссылки отображаются условно.
 * 
 * Основное поведение:
 * - Если пользователь находится на страницах "/storage" или "/adminpanel", 
 *   отображается только кнопка "Выход", которая ведет на главную страницу.
 * - На других страницах (Главная, Вход, Регистрация) соответствующие ссылки будут видимы.
 * 
 * Пропсы:
 * @param {Function} onLogout - Функция, вызываемая при выходе пользователя.
 * @param {boolean} isAuthenticated - Флаг, указывающий, аутентифицирован ли пользователь.
 *
 * Использует хук useLocation из react-router-dom для получения текущего пути.
 * 
 * Доступные ссылки:
 * - Главная ("/")
 * - Вход ("/signin")
 * - Регистрация ("/signup")
 */
export const Navbar = ({ onLogout, isAuthenticated }: { onLogout: () => void; isAuthenticated: boolean }) => {
    const location = useLocation();
    const showExitButtonOnly = location.pathname === '/storage' || location.pathname === '/adminpanel';
    
    return (
        <nav>
            <ul className="nav-ul">
                {showExitButtonOnly ? (
                    <li className="nav-ul-li" onClick={onLogout}>
                        <Link to="/">Выход</Link>
                    </li>
                ) : (
                    <>
                        {isAuthenticated ? ( // Проверяем, аутентифицирован ли пользователь
                            <>
                                <li className="nav-ul-li"><Link to="/storage">Файловое хранилище</Link></li>
                                <li className="nav-ul-li" onClick={onLogout}>Выход</li>
                            </>
                        ) : (
                            <>
                                {location.pathname !== '/' && (
                                    <li className="nav-ul-li"><Link to="/">Главная</Link></li>
                                )}
                                {location.pathname !== '/signin' && (
                                    <li className="nav-ul-li"><Link to="/signin">Вход</Link></li>
                                )}
                                {location.pathname !== '/signup' && (
                                    <li className="nav-ul-li"><Link to="/signup">Регистрация</Link></li>
                                )}
                            </>
                        )}
                    </>
                )}
            </ul>
        </nav>
    );
};
