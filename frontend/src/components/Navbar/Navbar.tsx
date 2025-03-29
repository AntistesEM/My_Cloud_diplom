import { Link, useLocation } from "react-router-dom";

/**
 * Navbar - компонент навигационной панели.
 *
 * Компонент отображает навигационные ссылки на разные страницы приложения.
 * В зависимости от текущего пути (location.pathname) и роли пользователя, ссылки отображаются условно.
 * 
 * Основное поведение:
 * - Если пользователь находится на страницах "/storage" или "/admin", 
 *   отображается только кнопка "Выход", которая ведет на главную страницу.
 * - На других страницах (Главная, Вход, Регистрация) соответствующие ссылки будут видимы.
 * 
 * Пропсы:
 * @param {Function} onLogout - Функция, вызываемая при выходе пользователя из системы.
 * @param {boolean} isAuthenticated - Флаг, указывающий, аутентифицирован ли пользователь.
 * @param {string} role - Роль пользователя, которая влияет на отображение ссылок.
 *
 * Использует хук useLocation из react-router-dom для получения текущего пути.
 * 
 * Доступные ссылки:
 * - Главная ("/")
 * - Вход ("/signin")
 * - Регистрация ("/signup")
 */
export const Navbar = ({ onLogout, role }: { onLogout: () => void; role: string }) => {
    const location = useLocation();
    
    return (
        <nav>
            <ul className="nav-ul">
                {location.pathname === '/admin' ? (
                    <li className="nav-ul-li" onClick={onLogout}>
                        <Link to="/">Выход</Link>
                    </li>
                ) : (
                    <>
                        {(role === 'admin' && location.pathname.startsWith('/storage/')) ? (
                            <>                                
                                <li className="nav-ul-li">
                                    <Link to='/admin'>Назад</Link>
                                </li>
                                <li className="nav-ul-li" onClick={onLogout}>
                                    <Link to="/">Выход</Link>
                                </li>
                            </>
                            ) : ((role !== 'admin' && location.pathname.startsWith('/storage/')) ? (
                                    <li className="nav-ul-li" onClick={onLogout}>
                                        <Link to="/">Выход</Link>
                                    </li>
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
                                )
                            )
                        }
                    </>
                )}
            </ul>
        </nav>
    );
};
