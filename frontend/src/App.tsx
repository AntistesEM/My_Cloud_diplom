import './App.css';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { useEffect, useState } from 'react';
import { LoginForm } from './components/LoginForm';
import { RegistrationForm } from './components/RegistrationForm';
// import { AdminPanel } from './components/AdminPanel';  // WIP: Панель администратора в разработке
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
 *   - Файловое хранилище ("/storage"): в разработке.
 *   - Панель администратора ("/adminpanel"): в разработке.
 * 
 * Компонент также управляет состоянием аутентификации пользователя, используя
 * состояние `isAuthenticated`, которое обновляется при загрузке приложения и после выхода
 * пользователя из системы.
 * 
 * @returns {JSX.Element} - Возвращает JSX, представляющий главный интерфейс приложения с навигацией и маршрутами.
 */
const App = () => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem('token')); // Устанавливаем статус аутентификации

    // Функция выхода из системы
    const handleLogout = () => {
        localStorage.removeItem('token'); // Удаляем токен из localStorage
        localStorage.removeItem('role'); // Удаляем информацию о роли
        setIsAuthenticated(false); // Устанавливаем статус аутентификации в false
    };
    // проверяем наличие токена при загрузке приложения
    useEffect(() => {
        const token = localStorage.getItem('token'); // Проверяем наличие токена
        setIsAuthenticated(!!token); // Обновляем статус аутентификации
    }, []);

    return (
        <Router>
            <Navbar onLogout={handleLogout} isAuthenticated={isAuthenticated} />
            <Routes>
                <Route path="/" element={
                    <div className="wrap">
                        <h1>Облачное хранилище My Cloud</h1>
                        <p>Приложение позволяет пользователям отображать, загружать, отправлять, скачивать и переименовывать файлы.</p>
                        <p>Выберите действие для продолжения</p>
                    </div>
                } />
                <Route path="/signin" element={<LoginForm />} />
                <Route path="/signup" element={<RegistrationForm />} />
                <Route path="/storage" element={
                    <ProtectedRoute> {/* Защищенный маршрут для файлового хранилища */}
                        <FileStorage />
                    </ProtectedRoute>
                } />
                {/* <Route path="/admin" element={  // WIP: Панель администратора в разработке
                    <ProtectedRoute>
                        <AdminPanel />
                    </ProtectedRoute>
                } /> */}
            </Routes>
        </Router>
    );
};

export default App
