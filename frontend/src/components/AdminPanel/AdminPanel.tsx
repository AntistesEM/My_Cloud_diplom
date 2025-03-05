import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import './AdminPanel.css';

// Определение типа пользователя
interface User {
    id: number;
    fullName: string;
    role: string;
    storageFiles: [{size: number}];
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

    // Хук для навигации между страницами.
    const navigate = useNavigate();

    // Хук, который выполняется при монтировании компонента.
    useEffect(() => {
        // Функция для загрузки пользователей с сервера.
        const fetchUsers = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/users');

                if (!response.ok) {
                    throw new Error('Ошибка при загрузке пользователей');
                }

                const data: User[] = await response.json();

                // Устанавливаем полученный список пользователей в состояние.
                setUsers(data);
            } catch (error) {
                console.error(error);
            }
        };

        fetchUsers();
    }, []);

    /**
     * handleDeleteUser - функция для удаления пользователя по ID.
     * @param {number} userId - ID пользователя, которого нужно удалить.
     */
    const handleDeleteUser = async (userId: number) => {  
        try {
            const response = await fetch(`http://localhost:5000/api/users/delete/${userId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error('Ошибка при удалении пользователя');
            }

            const data = users.filter(user => user.id !== userId);

            setUsers(data);
        } catch (error) {
            console.error(error);
        }
    };

    /**
     * toggleAdmin - функция для изменения роли пользователя (на админа или обратно).
     * @param {number} userId - ID пользователя, роль которого нужно изменить.
     * @param {string} newRole - новая роль для пользователя (например, "user" или "admin").
     */
    const toggleAdmin = async (userId: number, newRole: string) => {
        try {
            const response = await fetch(`http://localhost:5000/api/users/toggle/${userId}`, {
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

            setUsers(users.map(user => user.id === userId ? { ...user, role: updatedRole.role } : user));
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="admin-panel">
            <h2 className="admin-panel__title">Администраторы и пользователи</h2>
    
            <ul className="admin-panel__list">
                {users.map(user => {
                    const totalFileSize = user.storageFiles.reduce((total, file) => (
                        total + (file.size || 0)
                    ), 0);
    
                    return (
                        <li key={user.id} className="admin-panel__item">
                            {Object.entries(user).map(([key, value]) => (
                                (key !== 'password' && key !== 'id') && (
                                    (key !== 'storageFiles') ? (
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
                            <button className="admin-panel__button" onClick={() => navigate(`/storage/${user.id}`)}>Хранилище</button>
                            <button className="admin-panel__button" onClick={() => {
                                const newRole = prompt('Введите новую роль:', user.role);
                                if (newRole) toggleAdmin(user.id, newRole);
                            }}>Изменить роль</button>
                            <button className="admin-panel__button" onClick={() => handleDeleteUser(user.id)}>Удалить</button>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};

export default AdminPanel;
