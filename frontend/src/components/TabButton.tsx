import * as React from 'react';
import { TabType } from '../types';

interface NavItemProps {
    tab: TabType;
    icon: React.ReactNode;
    label: string;
    isSelected: boolean;
    onClick: (tab: TabType) => void;
    className?: string;
}

const NavItem: React.FC<NavItemProps> = ({
    tab,
    icon,
    label,
    isSelected,
    onClick,
    className = ''
}) => (
    <div className={`mb-4 ${className}`}>
        <button 
            onClick={() => onClick(tab)}
            className={`
                p-2 rounded w-full
                transition-colors duration-200
                focus:outline-none focus:ring-2 focus:ring-blue-500
                ${isSelected ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}
            `}
        >
            {icon}
            <span className="ml-2">{label}</span>
        </button>
    </div>
);

export default NavItem;