import { Navigate } from "react-router-dom";

/**
 * Компонент ProtectedRoute обеспечивает защиту маршрутов для аутентифицированных пользователей.
 * 
 * @param {Object} props - Свойства компонента.
 * @param {React.ReactNode} props.children - Дочерние компоненты, которые будут рендериться, если доступ разрешен.
 * @param {boolean} [props.requireAdmin=false] - Опциональный параметр, указывающий, требуется ли роль администратора для доступа к маршруту.
 * 
 * Если токен отсутствует, пользователя перенаправляют на страницу входа.
 * Если требуется роль администратора и текущая роль пользователя не является администратором, происходит перенаправление на страницу "/storage".
 * 
 * @returns {JSX.Element} - Возвращает дочерние компоненты или выполняет перенаправление.
 */
export const ProtectedRoute: React.FC<{ children: React.ReactNode, requireAdmin?: boolean }> = ({ children, requireAdmin }) => { 
    const token = localStorage.getItem('token'); 
    const role = localStorage.getItem('role');

    if (!token) {
        return <Navigate to="/signin" />;
    }
    
    if (requireAdmin && role !== 'admin') {
        return <Navigate to="/storage" />;
    }

    return <>{children}</>;
};
