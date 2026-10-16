# cau_hinh_giao_dien.py
"""
HỆ THỐNG GIAO DIỆN HIỆN ĐẠI (MODERN DESIGN SYSTEM - FLUENT / SLATE 2026)
Áp dụng chuẩn thiết kế tối giản, sạch sẽ, phân tầng thị giác (Visual Hierarchy)
Tông màu chủ đạo: Slate 50-900 & Electric Royal Blue (#2563EB)
"""

def lay_style_xanh_nuoc_bien():
    return """
    /* =========================================================================
       1. NỀN ỨNG DỤNG & CỬA SỔ CHÍNH (CANVAS)
       ========================================================================= */
    QMainWindow, QWidget#CentralWidget, QDialog, QMessageBox { 
        background-color: #F8FAFC; 
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif; 
        color: #0F172A;
    }

    /* =========================================================================
       2. MENU BÊN TRÁI (LEFT SIDEBAR NAVIGATION)
       ========================================================================= */
    QFrame#KhungTrai { 
        background-color: #FFFFFF; 
        border-right: 1px solid #E2E8F0; 
    }

    /* Nút Tab Điều hướng trên Sidebar */
    QPushButton.TabButton { 
        background-color: transparent; 
        color: #475569; 
        text-align: left; 
        padding: 11px 16px; 
        font-size: 13px; 
        font-weight: 600; 
        border: none; 
        border-radius: 8px; 
        margin: 3px 10px; 
    }
    QPushButton.TabButton:hover { 
        background-color: #F1F5F9; 
        color: #0F172A; 
    }
    QPushButton.TabButton:checked { 
        background-color: #EFF6FF; 
        color: #1D4ED8; 
        font-weight: 700;
        border-left: 4px solid #2563EB; 
        border-top-left-radius: 2px; 
        border-bottom-left-radius: 2px; 
    }

    /* Nút Thu gọn Menu */
    QPushButton#BtnThuGon { 
        background-color: transparent; 
        color: #94A3B8; 
        text-align: left; 
        padding: 10px 14px; 
        font-size: 12px; 
        font-weight: 600; 
        border: none; 
        border-radius: 6px; 
        margin: 4px 10px; 
    }
    QPushButton#BtnThuGon:hover { 
        background-color: #F1F5F9; 
        color: #475569; 
    }

    /* =========================================================================
       3. KHỐI CHỨA NỘI DUNG (CARDS)
       ========================================================================= */
    QFrame.CardWidget { 
        background-color: #FFFFFF; 
        border: 1px solid #E2E8F0; 
        border-radius: 12px; 
    }

    /* =========================================================================
       4. TIÊU ĐỀ & TYPOGRAPHY
       ========================================================================= */
    QLabel.TitleLabel { 
        color: #0F172A; 
        font-size: 18px; 
        font-weight: 800; 
        letter-spacing: -0.3px;
    }
    QLabel.SubtitleLabel { 
        color: #1E3A8A; 
        font-weight: 700; 
        font-size: 14px; 
        margin-bottom: 2px;
    }

    /* =========================================================================
       5. NÚT BẤM (BUTTONS)
       ========================================================================= */
    QPushButton.ActionBtn { 
        color: white; 
        background-color: #2563EB; 
        border-radius: 6px; 
        padding: 8px 16px; 
        font-weight: 700; 
        font-size: 13px; 
        border: none; 
    }
    QPushButton.ActionBtn:hover { 
        background-color: #1D4ED8; 
    }
    QPushButton.ActionBtn:pressed { 
        background-color: #1E40AF; 
    }

    /* =========================================================================
       6. TABS NỘI DUNG (QTabWidget & QTabBar)
       ========================================================================= */
    QTabWidget::pane { 
        border: 1px solid #E2E8F0; 
        background-color: #FFFFFF; 
        border-radius: 8px; 
    }
    QTabBar::tab { 
        background-color: #F1F5F9; 
        color: #64748B; 
        padding: 9px 18px; 
        border-top-left-radius: 8px; 
        border-top-right-radius: 8px; 
        margin-right: 3px; 
        font-weight: 600; 
        font-size: 13px;
        border: 1px solid transparent; 
    }
    QTabBar::tab:selected { 
        background-color: #FFFFFF; 
        color: #2563EB; 
        font-weight: 700;
        border: 1px solid #E2E8F0; 
        border-bottom: 2px solid #2563EB; 
    }
    QTabBar::tab:hover:!selected { 
        background-color: #E2E8F0; 
        color: #0F172A;
    }

    /* =========================================================================
       7. BẢNG DỮ LIỆU (QTableWidget & QTableView)
       ========================================================================= */
    QTableWidget { 
        background-color: #FFFFFF; 
        border: 1px solid #E2E8F0; 
        border-radius: 8px;
        gridline-color: transparent; 
        selection-background-color: #EFF6FF; 
        selection-color: #1E40AF; 
        font-size: 13px; 
    }
    QTableWidget::item { 
        padding: 8px 10px; 
        border-bottom: 1px solid #F1F5F9; 
    }
    QTableWidget::item:hover { 
        background-color: #F8FAFC; 
    }
    QTableWidget::item:selected { 
        background-color: #EFF6FF; 
        color: #1E40AF; 
    }

    QHeaderView::section { 
        background-color: #F8FAFC; 
        color: #475569; 
        font-weight: 700; 
        font-size: 12px;
        border: none; 
        border-bottom: 2px solid #E2E8F0; 
        padding: 10px 8px; 
        text-align: left; 
    }

    /* =========================================================================
       8. CÁC Ô NHẬP LIỆU (INPUTS, COMBOBOX, TEXTEDIT)
       ========================================================================= */
    QLineEdit, QComboBox, QTextEdit { 
        background-color: #FFFFFF; 
        color: #0F172A; 
        border: 1px solid #CBD5E1; 
        border-radius: 6px; 
        padding: 7px 10px; 
        font-size: 13px; 
    }
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus { 
        border: 2px solid #2563EB; 
        background-color: #FFFFFF; 
    }
    QComboBox::drop-down { 
        subcontrol-origin: padding; 
        subcontrol-position: top right; 
        width: 24px; 
        border-left: none; 
        background: transparent; 
    }
    QComboBox QAbstractItemView { 
        background-color: #FFFFFF; 
        border: 1px solid #CBD5E1; 
        border-radius: 6px; 
        selection-background-color: #EFF6FF; 
        selection-color: #1D4ED8; 
        padding: 4px; 
        outline: none; 
    }

    /* =========================================================================
       9. HỘP KIỂM (QCheckBox)
       ========================================================================= */
    QCheckBox { 
        font-size: 13px; 
        color: #334155; 
        spacing: 8px; 
    }
    QCheckBox::indicator { 
        width: 17px; 
        height: 17px; 
        border: 1.5px solid #CBD5E1; 
        border-radius: 4px; 
        background-color: #FFFFFF; 
    }
    QCheckBox::indicator:hover { 
        border-color: #2563EB; 
    }
    QCheckBox::indicator:checked { 
        background-color: #2563EB; 
        border-color: #2563EB; 
    }

    /* =========================================================================
       10. THANH CUỘN LƯỚT ÊM (MINIMAL SCROLLBARS)
       ========================================================================= */
    QScrollBar:vertical { 
        border: none; 
        background: #F8FAFC; 
        width: 8px; 
        border-radius: 4px; 
    }
    QScrollBar::handle:vertical { 
        background: #CBD5E1; 
        border-radius: 4px; 
        min-height: 25px; 
    }
    QScrollBar::handle:vertical:hover { 
        background: #94A3B8; 
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
        border: none; 
        background: none; 
    }

    QScrollBar:horizontal { 
        border: none; 
        background: #F8FAFC; 
        height: 8px; 
        border-radius: 4px; 
    }
    QScrollBar::handle:horizontal { 
        background: #CBD5E1; 
        border-radius: 4px; 
        min-width: 25px; 
    }
    QScrollBar::handle:horizontal:hover { 
        background: #94A3B8; 
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { 
        border: none; 
        background: none; 
    }

    /* =========================================================================
       11. BỘ PHÂN CHIA KHÔNG GIAN (SPLITTER)
       ========================================================================= */
    QSplitter::handle { 
        background-color: #E2E8F0; 
    }
    """