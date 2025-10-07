// Этот файл определяет визуальные параметры для каждой темы.
export const themes = {
  default: {
    name: 'Стандартная',
    styles: {
      '--bg-color': '#f4f7fa',
      '--text-color': '#333333',
      '--font-family': 'Arial, sans-serif',
      '--bg-image': 'none',
      '--card-bg-color': '#ffffff',
      '--border-color': '#dee2e6',
      '--primary-color': '#007bff',
      '--primary-text-color': '#ffffff',
      '--secondary-color': '#dc3545',
      '--secondary-text-color': '#ffffff',
      '--edit-color': '#ffc107',
      '--edit-text-color': '#212529',
    }
  },
  lavender: {
    name: 'Нежный лавандовый',
    styles: {
      '--bg-color': '#E6E6FA',
      '--text-color': '#4B0082',
      '--font-family': "'Georgia', serif",
      '--bg-image': 'none',
      '--card-bg-color': 'rgba(255, 255, 255, 0.8)',
      '--border-color': '#D8BFD8',
      '--primary-color': '#8A2BE2',
      '--primary-text-color': '#ffffff',
      '--secondary-color': '#BA55D3',
      '--secondary-text-color': '#ffffff',
      '--edit-color': '#DDA0DD',
      '--edit-text-color': '#4B0082',
    }
  },
  mint: {
    name: 'Свежий мятный',
    styles: {
      '--bg-color': '#F0FFF0',
      '--text-color': '#006400',
      '--font-family': "'Verdana', sans-serif",
      '--bg-image': 'none',
      '--card-bg-color': 'rgba(255, 255, 255, 0.85)',
      '--border-color': '#98FB98',
      '--primary-color': '#2E8B57',
      '--primary-text-color': '#ffffff',
      '--secondary-color': '#FF6347',
      '--secondary-text-color': '#ffffff',
      '--edit-color': '#90EE90',
      '--edit-text-color': '#006400',
    }
  },
  sunny: {
    name: 'Солнечный оранжевый',
    styles: {
      '--bg-color': '#FFF5E1',
      '--text-color': '#D2691E',
      '--font-family': "'Helvetica Neue', sans-serif",
      '--bg-image': 'none',
      '--card-bg-color': 'rgba(255, 255, 255, 0.8)',
      '--border-color': '#FFDAB9',
      '--primary-color': '#FF8C00',
      '--primary-text-color': '#ffffff',
      '--secondary-color': '#FF4500',
      '--secondary-text-color': '#ffffff',
      '--edit-color': '#FFD700',
      '--edit-text-color': '#8B4513',
    }
  },
  coffee: {
    name: 'Кофейный бежевый',
    styles: {
      '--bg-color': '#F5F5DC',
      '--text-color': '#8B4513',
      '--font-family': "'Courier New', monospace",
      '--bg-image': 'none',
      '--card-bg-color': 'rgba(255, 253, 246, 0.85)',
      '--border-color': '#D2B48C',
      '--primary-color': '#A0522D',
      '--primary-text-color': '#ffffff',
      '--secondary-color': '#800000',
      '--secondary-text-color': '#ffffff',
      '--edit-color': '#DEB887',
      '--edit-text-color': '#8B4513',
    }
  },
  navy: {
    name: 'Темно-синий',
    styles: {
      '--bg-color': '#000080',
      '--text-color': '#FFFFFF', // Белый текст
      '--font-family': "'Times New Roman', serif",
      '--bg-image': 'none',
      // --- ИЗМЕНЕНИЯ ЗДЕСЬ ---
      '--card-bg-color': 'rgba(25, 25, 112, 0.7)', // Фон карточки - полупрозрачный темно-синий
      '--border-color': '#4682B4', // Цвет границ - стальной синий
      '--primary-color': '#4169E1', // Основной цвет - королевский синий
      '--primary-text-color': '#ffffff',
      '--secondary-color': '#B22222', // Второстепенный (удалить) - кирпичный
      '--secondary-text-color': '#ffffff',
      '--edit-color': '#ADD8E6', // Цвет редактирования - светло-синий
      '--edit-text-color': '#000080', // Текст на кнопке ред. - темно-синий
    }
  }
};