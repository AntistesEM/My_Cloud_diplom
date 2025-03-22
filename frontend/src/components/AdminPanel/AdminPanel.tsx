import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import './AdminPanel.css';

// Определение типа пользователя
interface User {
    id_user: number;
    email: string;
    username: string;
    fullname: string;
    role: string;
    storages: File[];
}

interface File {
    id_file: number;
    original_name: string;
    size: number;
}

/**
 * AdminPanel - компонент, который отображает список пользователей
 * и предоставляет возможность управления пользователями 
 * (удаление, изменение роли, просмотр файлового хранилища).
 * 
 * return (<AdminPanel />)
 */
export const AdminPanel: React.FC = () => {
    // Используем состояние для хранения списка пользователей.
    const [users, setUsers] = useState<User[]>([]);
    // const { id_user } = useParams<{ id_user: string }>(); // Получаем ID пользователя из URL

    // Хук для навигации между страницами.
    const navigate = useNavigate();
    
    // Функция для загрузки пользователей с сервера.
    const fetchUsers = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/users');

            if (!response.ok) {
                throw new Error('Ошибка при загрузке пользователей');
            }

            const data: User[] = await response.json();
            
            // Сортируем пользователей: admin сначала, затем остальные в алфавитном порядке
            const sortedUsers = data.sort((a, b) => {
                // Проверяем: admin ли пользователь, и если да, то возвращаем -1, чтобы он был первым
                if (a.role === 'admin' && b.role !== 'admin') return -1; 
                if (a.role !== 'admin' && b.role === 'admin') return 1;

                // Если роли одинаковые, сортируем по fullname
                return a.username.localeCompare(b.username);
            });

            // Устанавливаем полученный список пользователей в состояние.
            setUsers(sortedUsers);
        } catch (error) {
            console.error(error);
        }
    };

    // Вызывается при загрузке компонента
    useEffect(() => {
        fetchUsers();
    }, []);

    /**
     * handleDeleteUser - функция для удаления пользователя по ID.
     * @param {number} id_user - ID пользователя, которого нужно удалить.
     */
    const handleDeleteUser = async (id_user: number) => {
        try {
            const response = await fetch(`http://localhost:8000/api/users/${id_user}/`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error('Ошибка при удалении пользователя');
            }

            const newData = users.filter(user => user.id_user !== Number(id_user));

            setUsers(newData);
        } catch (error) {
            console.error(error);
        }
    };


    /**
     * toggleAdmin - функция для изменения роли пользователя (на админа или обратно).
     * @param {number} id_user - ID пользователя, роль которого нужно изменить.
     * @param {string} newRole - новая роль для пользователя (например, "user" или "admin").
     */
    const toggleAdmin = async (id_user: number, newRole: string) => {
        try {
            const response = await fetch(`http://localhost:8000/api/users/${id_user}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ role: newRole }),
            });

            if (!response.ok) {
                throw new Error('Ошибка при изменении роли пользователя');
            }

            const updatedRole = await response.json();

            setUsers(users.map(user => user.id_user === id_user ? { ...user, role: updatedRole.role } : user));
            
            // После изменения роли заново загружаем пользователей
            await fetchUsers();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="admin-panel">
            <h2 className="admin-panel__title">Администраторы и пользователи</h2>
    
            <ul className="admin-panel__list">
                {users.map(user => {
                    const totalFileSize = user.storages.reduce((total, file) => (
                        total + (file.size || 0)
                    ), 0);
    
                    return (
                        <li key={user.id_user} className="admin-panel__item">
                            {Object.entries(user).map(([key, value]) => (
                                (key !== 'password_hash' && key !== 'id_user') && (
                                    (key !== 'storages') ? (
                                        <div key={key}>
                                            <strong>{key}:</strong> {value}
                                        </div>
                                    ) : (
                                        <div key={key}>
                                            <strong>{key}:</strong> {` ${value.length} files; Total Size: ${totalFileSize} bytes`}
                                        </div>
                                    )
                                )
                            ))}
                            <button className="admin-panel__button" onClick={() => navigate(`/storage/${user.id_user}`)}>Хранилище</button>
                            <button className="admin-panel__button" onClick={() => {
                                const newRole = prompt('Введите новую роль:', user.role);
                                if (newRole) toggleAdmin(user.id_user, newRole);
                            }}>Изменить роль</button>
                            <button className="admin-panel__button" onClick={() => handleDeleteUser(user.id_user)}>Удалить</button>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};

export default AdminPanel;
