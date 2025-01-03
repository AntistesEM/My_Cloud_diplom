import './App.css';

import { BrowserRouter as Router, Route, Routes, Link, useLocation } from "react-router-dom";
import { LoginForm } from './components/LoginForm';
import { RegistrationForm } from './components/RegistrationForm';
// import { AdminPanel } from './components/AdminPanel';  // WIP: Панель администратора в разработке
// import { FileStorage } from './components/FileStorage';  // WIP: Файловое хранилище в разработке

/**
 * Navbar компонент
 * 
 * Компонент навигационной панели, который отображает ссылки на разные страницы приложения.
 * Ссылки отображаются условно, в зависимости от текущего пути (location.pathname).
 * Если пользователь находится на одной из страниц (Главная, Вход или Регистрация),
 * соответствующая ссылка не отображается.
 * 
 * Использует хук useLocation из react-router-dom для получения текущего пути.
 * 
 * Ссылки:
 * - Главная ("/")
 * - Вход ("/signin")
 * - Регистрация ("/signup")
 */
const Navbar = () => {
  const location = useLocation(); // Получаем текущий путь

  return (
      <nav>
          <ul className="nav-ul">
              {/* Проверяем, не находимся ли мы на определенной странице, если да то скрываем кнопку-ссылку на нее */}
              {location.pathname !== '/' && (
                  <li className="nav-ul-li"><Link to="/">Главная</Link></li>
              )}
              {location.pathname !== '/signin' && (
                  <li className="nav-ul-li"><Link to="/signin">Вход</Link></li>
              )}
              {location.pathname !== '/signup' && (
                  <li className="nav-ul-li"><Link to="/signup">Регистрация</Link></li>
              )}
          </ul>
      </nav>
  );
};

/**
 * App компонент
 * 
 * Главный компонент приложения, который отвечает за маршрутизацию и отображение
 * различных страниц. Использует библиотеку react-router-dom для управления маршрутами.
 * 
 * Структура приложения включает в себя:
 * - Navbar: навигационная панель с ссылками на разные страницы.
 * - Routes: определяет маршруты для следующих страниц:
 *   - Главная ("/"): отображает приветственное сообщение и краткое описание функционала приложения.
 *   - Вход ("/signin"): отображает форму для входа пользователя.
 *   - Регистрация ("/signup"): отображает форму для регистрации нового пользователя.
 * 
 * Временные маршруты (WIP):
 * - Панель администратора ("/adminpanel"): в разработке.
 * - Файловое хранилище ("/storage"): в разработке.
 */
const App = () => {
  return (
      <Router>
          <Navbar />
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
              {/* <Route path="/adminpanel" element={<AdminPanel />} />  // WIP: Панель администратора в разработке */}
              {/* <Route path="/storage" element={<FileStorage />} />  // WIP: Файловое хранилище в разработке */}
          </Routes>
      </Router>
  );
};

export default App
