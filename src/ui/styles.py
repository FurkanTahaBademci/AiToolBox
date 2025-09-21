"""
Modern AI ToolBox Stylesheet
Gelişmiş okunabilirlik ve modern tasarım için CSS stilleri
"""

class AppStyles:
    """Uygulama stilleri sınıfı"""
    
    # Ana renk paleti
    COLORS = {
        'primary': '#007ACC',
        'primary_hover': '#005a9e',
        'primary_pressed': '#004578',
        'primary_dark': '#005a9e',      # Alias for hover
        'primary_darker': '#004578',    # Alias for pressed
        'primary_light': '#66b3ff',     # Yeni eklendi
        'secondary': '#6c757d',
        'success': '#28a745',
        'danger': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#212529',
        'white': '#ffffff',
        'gray_50': '#fafafa',           # Yeni eklendi
        'gray_100': '#f8f9fa',
        'gray_200': '#e9ecef',
        'gray_300': '#dee2e6',
        'gray_400': '#ced4da',
        'gray_500': '#adb5bd',
        'gray_600': '#6c757d',
        'gray_700': '#495057',
        'gray_800': '#343a40',
        'gray_900': '#212529',
        'hover': '#f0f2f5',            # Hover background color
        'surface': '#f8f9fa',          # Surface background
        'border': '#dee2e6',           # Border color
        'text': '#212529'              # Primary text color
    }
    
    # Font ayarları
    FONTS = {
        'family_primary': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
        'family_mono': 'Consolas, Monaco, "Courier New", monospace',
        'size_title': '28px',
        'size_heading': '16px',
        'size_body': '13px',
        'size_small': '11px',
        'weight_normal': 'normal',
        'weight_bold': 'bold'
    }
    
    @staticmethod
    def get_main_window_style():
        """Ana pencere stili"""
        return f"""
            QMainWindow {{
                background-color: {AppStyles.COLORS['light']};
                font-family: {AppStyles.FONTS['family_primary']};
            }}
        """
    
    @staticmethod
    def get_group_box_style():
        """Grup kutuları stili"""
        return f"""
            QGroupBox {{
                font-weight: {AppStyles.FONTS['weight_bold']};
                font-size: 15px;
                border: 2px solid {AppStyles.COLORS['gray_400']};
                border-radius: 10px;
                margin-top: 1.2ex;
                padding-top: 15px;
                background-color: {AppStyles.COLORS['white']};
                color: {AppStyles.COLORS['gray_900']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 15px;
                background-color: {AppStyles.COLORS['white']};
                color: {AppStyles.COLORS['gray_900']};
                border-radius: 5px;
                border: 2px solid {AppStyles.COLORS['gray_400']};
                font-weight: {AppStyles.FONTS['weight_bold']};
                font-size: 14px;
            }}
        """
    
    @staticmethod
    def get_label_style():
        """Label stilleri"""
        return f"""
            QLabel {{
                color: {AppStyles.COLORS['gray_800']};
                font-size: {AppStyles.FONTS['size_body']};
                font-family: {AppStyles.FONTS['family_primary']};
                font-weight: {AppStyles.FONTS['weight_bold']};
            }}
        """
    
    @staticmethod
    def get_title_label_style():
        """Başlık label stili"""
        return f"""
            QLabel {{
                font-size: {AppStyles.FONTS['size_title']};
                font-weight: {AppStyles.FONTS['weight_bold']};
                color: {AppStyles.COLORS['dark']};
                margin-bottom: 15px;
                font-family: {AppStyles.FONTS['family_primary']};
            }}
        """
    
    @staticmethod
    def get_input_style():
        """Input alanları stili"""
        return f"""
            QLineEdit, QSpinBox, QComboBox {{
                padding: 12px 15px;
                min-height: 20px;
                max-height: 45px;
                border: 2px solid {AppStyles.COLORS['gray_400']};
                border-radius: 8px;
                background-color: {AppStyles.COLORS['white']};
                font-size: {AppStyles.FONTS['size_body']};
                font-family: {AppStyles.FONTS['family_primary']};
                color: {AppStyles.COLORS['gray_900']};
                font-weight: {AppStyles.FONTS['weight_bold']};
                selection-background-color: {AppStyles.COLORS['primary']};
            }}
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border-color: {AppStyles.COLORS['primary']};
                outline: none;
                box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.1);
            }}
            QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {{
                background-color: {AppStyles.COLORS['gray_200']};
                color: {AppStyles.COLORS['gray_600']};
                border-color: {AppStyles.COLORS['gray_300']};
                font-weight: {AppStyles.FONTS['weight_normal']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                height: 100%;
                border-left-width: 1px;
                border-left-color: {AppStyles.COLORS['gray_400']};
                border-left-style: solid;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background-color: {AppStyles.COLORS['gray_100']};
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid {AppStyles.COLORS['gray_600']};
                width: 8px;
                height: 8px;
                border-top: none;
                border-right: none;
                transform: rotate(45deg);
                margin-top: -2px;
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid {AppStyles.COLORS['gray_400']};
                border-radius: 8px;
                background-color: {AppStyles.COLORS['white']};
                selection-background-color: {AppStyles.COLORS['primary']};
                selection-color: {AppStyles.COLORS['white']};
                padding: 8px;
                font-weight: {AppStyles.FONTS['weight_bold']};
                min-height: 25px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }}
            QSpinBox::up-arrow, QSpinBox::down-arrow {{
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }}
        """
    
    @staticmethod
    def get_progress_bar_style():
        """Progress bar stili"""
        return f"""
            QProgressBar {{
                border: 2px solid {AppStyles.COLORS['gray_300']};
                border-radius: 8px;
                background-color: {AppStyles.COLORS['gray_200']};
                text-align: center;
                font-size: {AppStyles.FONTS['size_body']};
                font-weight: {AppStyles.FONTS['weight_bold']};
                color: {AppStyles.COLORS['white']};
                height: 25px;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {AppStyles.COLORS['success']},
                    stop: 1 #20c997
                );
                border-radius: 6px;
                margin: 1px;
            }}
        """
    
    @staticmethod
    def get_text_edit_style():
        """Text edit stili"""
        return f"""
            QTextEdit {{
                border: 2px solid {AppStyles.COLORS['gray_300']};
                border-radius: 8px;
                background-color: {AppStyles.COLORS['white']};
                font-family: {AppStyles.FONTS['family_mono']};
                font-size: {AppStyles.FONTS['size_small']};
                color: {AppStyles.COLORS['gray_800']};
                padding: 8px;
                line-height: 1.4;
            }}
            QTextEdit:focus {{
                border-color: {AppStyles.COLORS['primary']};
            }}
        """
    
    @staticmethod
    def get_primary_button_style():
        """Birincil buton stili"""
        return f"""
            QPushButton {{
                background-color: {AppStyles.COLORS['primary']};
                color: {AppStyles.COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: {AppStyles.FONTS['weight_bold']};
                font-size: {AppStyles.FONTS['size_body']};
                padding: 12px 24px;
                font-family: {AppStyles.FONTS['family_primary']};
            }}
            QPushButton:hover {{
                background-color: {AppStyles.COLORS['primary_hover']};
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: {AppStyles.COLORS['primary_pressed']};
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background-color: {AppStyles.COLORS['gray_400']};
                color: {AppStyles.COLORS['gray_600']};
            }}
        """
    
    @staticmethod
    def get_secondary_button_style():
        """İkincil buton stili"""
        return f"""
            QPushButton {{
                background-color: {AppStyles.COLORS['white']};
                color: {AppStyles.COLORS['gray_700']};
                border: 2px solid {AppStyles.COLORS['gray_400']};
                border-radius: 8px;
                font-size: {AppStyles.FONTS['size_body']};
                padding: 12px 24px;
                font-family: {AppStyles.FONTS['family_primary']};
                font-weight: {AppStyles.FONTS['weight_normal']};
            }}
            QPushButton:hover {{
                background-color: {AppStyles.COLORS['gray_100']};
                border-color: {AppStyles.COLORS['gray_500']};
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: {AppStyles.COLORS['gray_200']};
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background-color: {AppStyles.COLORS['gray_200']};
                color: {AppStyles.COLORS['gray_500']};
                border-color: {AppStyles.COLORS['gray_300']};
            }}
        """
    
    @staticmethod
    def get_danger_button_style():
        """Tehlikeli buton stili"""
        return f"""
            QPushButton {{
                background-color: {AppStyles.COLORS['danger']};
                color: {AppStyles.COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: {AppStyles.FONTS['weight_bold']};
                font-size: {AppStyles.FONTS['size_body']};
                padding: 12px 24px;
                font-family: {AppStyles.FONTS['family_primary']};
            }}
            QPushButton:hover {{
                background-color: #c82333;
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: #bd2130;
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background-color: {AppStyles.COLORS['gray_400']};
                color: {AppStyles.COLORS['gray_600']};
            }}
        """
    
    @staticmethod
    def get_status_styles():
        """Durum mesajları stilleri"""
        return {
            'ready': f"""
                QLabel {{
                    color: {AppStyles.COLORS['success']};
                    font-weight: {AppStyles.FONTS['weight_bold']};
                    font-size: {AppStyles.FONTS['size_body']};
                    font-family: {AppStyles.FONTS['family_primary']};
                }}
            """,
            'processing': f"""
                QLabel {{
                    color: {AppStyles.COLORS['info']};
                    font-weight: {AppStyles.FONTS['weight_bold']};
                    font-size: {AppStyles.FONTS['size_body']};
                    font-family: {AppStyles.FONTS['family_primary']};
                }}
            """,
            'error': f"""
                QLabel {{
                    color: {AppStyles.COLORS['danger']};
                    font-weight: {AppStyles.FONTS['weight_bold']};
                    font-size: {AppStyles.FONTS['size_body']};
                    font-family: {AppStyles.FONTS['family_primary']};
                }}
            """,
            'warning': f"""
                QLabel {{
                    color: {AppStyles.COLORS['warning']};
                    font-weight: {AppStyles.FONTS['weight_bold']};
                    font-size: {AppStyles.FONTS['size_body']};
                    font-family: {AppStyles.FONTS['family_primary']};
                }}
            """,
            'info': f"""
                QLabel {{
                    color: {AppStyles.COLORS['secondary']};
                    font-style: italic;
                    font-size: {AppStyles.FONTS['size_body']};
                    font-family: {AppStyles.FONTS['family_primary']};
                }}
            """
        }
    
    @staticmethod
    def get_complete_stylesheet():
        """Tüm stilleri birleştiren ana stylesheet"""
        return f"""
            {AppStyles.get_main_window_style()}
            {AppStyles.get_group_box_style()}
            {AppStyles.get_label_style()}
            {AppStyles.get_input_style()}
            {AppStyles.get_progress_bar_style()}
            {AppStyles.get_text_edit_style()}
        """
    
    @staticmethod
    def get_button_style():
        """Normal buton stili"""
        return f"""
            QPushButton {{
                background-color: {AppStyles.COLORS['gray_200']};
                color: {AppStyles.COLORS['text']};
                border: 1px solid {AppStyles.COLORS['border']};
                border-radius: 6px;
                padding: 8px 16px;
                font-family: {AppStyles.FONTS['family_primary']};
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {AppStyles.COLORS['gray_300']};
            }}
            QPushButton:pressed {{
                background-color: {AppStyles.COLORS['gray_400']};
            }}
            QPushButton:disabled {{
                background-color: {AppStyles.COLORS['gray_100']};
                color: {AppStyles.COLORS['gray_500']};
            }}
        """
    
    @staticmethod
    def get_primary_button_style():
        """Ana (primary) buton stili"""
        return f"""
            QPushButton {{
                background-color: {AppStyles.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-family: {AppStyles.FONTS['family_primary']};
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {AppStyles.COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {AppStyles.COLORS['primary_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {AppStyles.COLORS['gray_300']};
                color: {AppStyles.COLORS['gray_500']};
            }}
        """
