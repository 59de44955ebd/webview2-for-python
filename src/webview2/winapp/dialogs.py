from .const import *
from .dlls import *
from .themes import *

class OPENFILENAMEW(Structure):
    def __init__(self, *args, **kwargs):
        super(OPENFILENAMEW, self).__init__(*args, **kwargs)
        self.lStructSize = sizeof(self)
    _fields_ = (
        ('lStructSize', DWORD),
        ('hwndOwner', HWND),
        ('hInstance', HINSTANCE),
        ('lpstrFilter', LPWSTR),
        ('lpstrCustomFilter', LPWSTR),
        ('nMaxCustFilter', DWORD),
        ('nFilterIndex', DWORD),
        ('lpstrFile', LPWSTR),
        ('nMaxFile', DWORD),
        ('lpstrFileTitle', LPWSTR),
        ('nMaxFileTitle', DWORD),
        ('lpstrInitialDir', LPCWSTR),
        ('lpstrTitle', LPCWSTR),
        ('Flags', DWORD),
        ('nFileOffset', WORD),
        ('nFileExtension', WORD),
        ('lpstrDefExt', LPCWSTR),
        ('lCustData', LPARAM),
        ('lpfnHook', LPVOID),  # DLGHOOKPROC
        ('lpTemplateName', LPCWSTR),
        ('pvReserved', LPVOID),
        ('dwReserved', DWORD),
        ('FlagsEx', DWORD),
    )

########################################
# Classic MessageBox, but themed
########################################
def show_message_box(hwnd = None, text = '', window_title = '', utype = MB_ICONINFORMATION | MB_OK, is_dark = False):
    if is_dark:

        ########################################
        #
        ########################################
        def msg_box_subclass_proc_callback(hwnd, msg, wparam, lparam, uidsubclass, dwrefdata):
            res = dark_dialog_handle_messages(hwnd, msg, wparam)
            if res:
                return res
            return comctl32.DefSubclassProc(hwnd, msg, wparam, lparam)

        dark_msg_box_subclass_proc = SUBCLASSPROC(msg_box_subclass_proc_callback)

        classname_buf = create_unicode_buffer(7)

        class ctx:
            hook = None

        ########################################
        #
        ########################################
        def _hook_proc(nCode, wParam, lParam):
            if nCode < 0:
                return user32.CallNextHookEx(ctx.hook, nCode, wParam, lParam)

            msg = cast(lParam, POINTER(CWPRETSTRUCT)).contents
            user32.GetClassNameW(msg.hwnd, classname_buf, 7)
            if classname_buf.value == '#32770':
                if msg.message == WM_INITDIALOG:
                    dwm_use_dark_mode(msg.hwnd, True)
                    comctl32.SetWindowSubclass(msg.hwnd, dark_msg_box_subclass_proc, 0, 0)

                    hwnd = user32.FindWindowExW(msg.hwnd, None, WC_BUTTON, None)
                    while hwnd:
                        uxtheme.SetWindowTheme(hwnd, 'DarkMode_Explorer', None)
                        hwnd = user32.FindWindowExW(msg.hwnd, hwnd, WC_BUTTON, None)

            return user32.CallNextHookEx(ctx.hook, nCode, wParam, lParam)

        hook_proc = HOOKPROC(_hook_proc)
        ctx.hook = user32.SetWindowsHookExW(WH_CALLWNDPROCRET, hook_proc, 0, kernel32.GetCurrentThreadId())
        res = user32.MessageBoxW(hwnd, text, window_title, utype)
        user32.UnhookWindowsHookEx(ctx.hook)
        return res
    else:
        return user32.MessageBoxW(hwnd, text, window_title, utype)

########################################
# Modern UWP MessageBox - if content contains \n\n, the text before is used as instruction
########################################
#    def show_message_box(hwnd = None, text = '', window_title = '', common_buttons = TDCBF_OK_BUTTON, icon = TD_INFORMATION_ICON):
#        parts = text.split('\n\n', 1)
#        if len(parts) > 1:
#            instruction, text = parts
#        else:
#            instruction = None
#        button_pressed = INT(0)
#        comctl32.TaskDialog(
#            hwnd,
#            None,
#            window_title,
#            instruction,
#            text,
#            common_buttons,
#            cast(c_void_p(icon & 0xFFFF), LPCWSTR),
#            byref(button_pressed)
#        )
#        return button_pressed.value

########################################
#
########################################
def show_open_file_dialog(
    hwnd = None,
    title = 'Open...',
    default_extension = '',
    filter_string = 'All Files (*.*)\0*.*\0\0',
    initial_path = ''
):
    file_buffer = create_unicode_buffer(initial_path, MAX_PATH)
    ofn = OPENFILENAMEW()
    ofn.hwndOwner = hwnd
    ofn.lpstrTitle = title
    ofn.lpstrFile = cast(file_buffer, LPWSTR)
    ofn.nMaxFile = MAX_PATH
    ofn.lpstrDefExt = default_extension
    ofn.lpstrFilter = cast(create_unicode_buffer(filter_string), c_wchar_p)
    ofn.Flags = OFN_ENABLESIZING | OFN_PATHMUSTEXIST
    ok = comdlg32.GetOpenFileNameW(byref(ofn))
    return file_buffer[:].split('\0', 1)[0] if ok else None

########################################
#
########################################
def show_save_file_dialog(
    hwnd = None,
    title = 'Save...',
    default_extension = '',
    filter_string = 'All Files (*.*)\0*.*\0\0',
    initial_path = '',
    flags = OFN_ENABLESIZING | OFN_OVERWRITEPROMPT,
    filter_index = 0,
):
    file_buffer = create_unicode_buffer(initial_path, MAX_PATH)
    ofn = OPENFILENAMEW()
    ofn.hwndOwner = hwnd
    ofn.lpstrTitle = title
    ofn.lpstrFile = cast(file_buffer, LPWSTR)
    ofn.nMaxFile = MAX_PATH
    ofn.lpstrDefExt = default_extension
    ofn.lpstrFilter = cast(create_unicode_buffer(filter_string), c_wchar_p)
    ofn.Flags = flags
    ofn.nFilterIndex = filter_index
    ok = comdlg32.GetSaveFileNameW(byref(ofn))
    return file_buffer[:].split('\0', 1)[0] if ok else None
