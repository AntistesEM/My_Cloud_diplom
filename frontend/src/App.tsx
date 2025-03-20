import './App.css';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { useEffect, useState } from 'react';
import { LoginForm } from './components/LoginForm';
import { RegistrationForm } from './components/RegistrationForm';
import { AdminPanel } from './components/AdminPanel';
import { FileStorage } from './components/FileStorage';
import { Navbar } from './components/Navbar';
import { ProtectedRoute } from './components/ProtectedRoute';

/**
 * Компонент App
 * 
 * Главный компонент приложения, который отвечает за маршрутизацию и отображение
 * различных страниц. Использует библиотеку `react-router-dom` для управления маршрутами.
 * 
 * Структура приложения включает в себя:
 * - Navbar: навигационная панель с ссылками на разные страницы приложения.
 * - Routes: определяет маршруты для следующих страниц:
 *   - Главная ("/"): отображает приветственное сообщение и краткое описание функционала приложения.
 *   - Вход ("/signin"): отображает форму для входа пользователя.
 *   - Регистрация ("/signup"): отображает форму для регистрации нового пользователя.
 *   - Файловое хранилище ("/storage"): защищенный маршрут для доступа к файлам пользователя.
 *   - Панель администратора ("/admin"): защищенный маршрут для доступа к административной панели.
 * 
 * Компонент также управляет состоянием аутентификации пользователя, используя
 * состояние `isAuthenticated`, которое обновляется при загрузке приложения и после выхода
 * пользователя из системы. Роль пользователя хранится в состоянии `role` и может 
 * использоваться для условной отрисовки компонентов.
 * 
 * @returns {JSX.Element} - Возвращает JSX, представляющий главный интерфейс приложения с навигацией и маршрутами.
 */
const App = () => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem('access_token')); // Устанавливаем статус аутентификации
    const [role, setRole] = useState<string>(localStorage.getItem('role') || ''); // Состояние для роли

    // Функция выхода из системы
    const handleLogout = () => {
        localStorage.removeItem('access_token'); // Удаляем токен из localStorage
        localStorage.removeItem('refresh_token'); // Удаляем токен из localStorage
        localStorage.removeItem('role'); // Удаляем информацию о роли
        setIsAuthenticated(false); // Устанавливаем статус аутентификации в false
        setRole(''); // Обновляем состояние роли
    };
    
    // Обновляет состояние аутентификации и роли пользователя при изменении
    const updateAuth = (authStatus: boolean, userRole: string) => {
        setIsAuthenticated(authStatus); // Обновляем статус аутентификации в состоянии
        setRole(userRole); // Устанавливаем новую роль пользователя
    };

    // проверяем наличие токена и роли при загрузке приложения (один раз при монтировании)
    useEffect(() => {
        const token = localStorage.getItem('access_token'); // Проверяем наличие токена
        const storedRole = localStorage.getItem('role'); // Проверяем наличие роли
        setIsAuthenticated(!!token); // Обновляем статус аутентификации
        if (storedRole) {
            setRole(storedRole); // Устанавливаем роль
        }
    }, []);

    return (
        <Router>
            <Navbar onLogout={handleLogout} isAuthenticated={isAuthenticated} role={role} />
            <Routes>
                <Route path="/" element={
                    <div className="wrap">
                        <h1>Облачное хранилище My Cloud</h1>
                        <p>Приложение позволяет пользователям отображать, загружать, отправлять, скачивать и переименовывать файлы.</p>
                        <p>Выберите действие для продолжения</p>
                    </div>
                } />
                <Route path="/signin" element={<LoginForm updateAuth={updateAuth} />} />
                <Route path="/signup" element={<RegistrationForm />} />
                <Route path="/storage/:id_user" element={
                    <ProtectedRoute> {/* Защищенный маршрут для файлового хранилища */}
                        <FileStorage />
                    </ProtectedRoute>
                } />
                <Route path="/admin" element={
                    <ProtectedRoute> {/* Защищенный маршрут для файлового хранилища */}
                        <AdminPanel />
                    </ProtectedRoute>
                } />
            </Routes>
        </Router>
    );
};

export default App
