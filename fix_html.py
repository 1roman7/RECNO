with open("recno-master/frontend/index.html", "r") as f:
    content = f.read()

# 1. Add Hysteria2 Protocol
search_protocol = """                            <option value="vmess">VMess</option>
                            <option value="trojan">Trojan</option>
                        </select>"""
replace_protocol = """                            <option value="vmess">VMess</option>
                            <option value="trojan">Trojan</option>
                            <option value="hysteria2">Hysteria 2</option>
                        </select>"""
content = content.replace(search_protocol, replace_protocol)

# 2. Add Fingerprints
search_fingerprint = """                            <option value="chrome">Chrome</option>
                            <option value="safari">Safari</option>
                            <option value="qq">QQ</option>
                            <option value="random">Random</option>
                        </select>"""
replace_fingerprint = """                            <option value="chrome">Chrome</option>
                            <option value="firefox">Firefox</option>
                            <option value="safari">Safari</option>
                            <option value="ios">iOS</option>
                            <option value="android">Android</option>
                            <option value="edge">Edge</option>
                            <option value="360">360</option>
                            <option value="qq">QQ</option>
                            <option value="random">Random</option>
                            <option value="randomized">Randomized</option>
                        </select>"""
content = content.replace(search_fingerprint, replace_fingerprint)

# 3. Add Translations safely
search_transl = """        const translations = {
            ru: {
                dashboard: "Дашборд", users: "Пользователи", settings: "Настройки", logs: "Логи",
                logout: "Выход", total_users: "Всего пользователей", add_user: "Добавить пользователя",
                no_users_yet: "Пользователей пока нет...", username: "Имя пользователя", status: "Статус",
                traffic: "Трафик", actions: "Действия", unlimited: "Безлимит", cancel: "Отмена", save: "Сохранить",
                sign_in_title: "Вход в панель", sign_in_btn: "Войти", password: "Пароль", invalid_login: "Неверный логин или пароль", server_error: "Ошибка подключения", success_login: "Успешный вход"
            },
            en: {
                dashboard: "Dashboard", users: "Users", settings: "Settings", logs: "Logs",
                logout: "Logout", total_users: "Total Users", add_user: "Add User",
                no_users_yet: "No users yet...", username: "Username", status: "Status",
                traffic: "Traffic", actions: "Actions", unlimited: "Unlimited", cancel: "Cancel", save: "Save",
                sign_in_title: "Sign in to panel", sign_in_btn: "Sign In", password: "Password", invalid_login: "Invalid credentials", server_error: "Connection error", success_login: "Success"
            }
        };"""

replace_transl = """        const translations = {
            ru: {
                dashboard: "Дашборд", users: "Пользователи", settings: "Настройки", logs: "Логи",
                logout: "Выход", total_users: "Всего пользователей", add_user: "Добавить пользователя",
                no_users_yet: "Пользователей пока нет...", username: "Имя пользователя", status: "Статус",
                traffic: "Трафик", actions: "Действия", unlimited: "Безлимит", cancel: "Отмена", save: "Сохранить",
                sign_in_title: "Вход в панель", sign_in_btn: "Войти", password: "Пароль", invalid_login: "Неверный логин или пароль", server_error: "Ошибка подключения", success_login: "Успешный вход",
                inbounds: "Подключения", custom_keys: "Свои ключи", add_inbound: "Добавить подключение", add_key: "Добавить ключ"
            },
            en: {
                dashboard: "Dashboard", users: "Users", settings: "Settings", logs: "Logs",
                logout: "Logout", total_users: "Total Users", add_user: "Add User",
                no_users_yet: "No users yet...", username: "Username", status: "Status",
                traffic: "Traffic", actions: "Actions", unlimited: "Unlimited", cancel: "Cancel", save: "Save",
                sign_in_title: "Sign in to panel", sign_in_btn: "Sign In", password: "Password", invalid_login: "Invalid credentials", server_error: "Connection error", success_login: "Success",
                inbounds: "Inbounds", custom_keys: "Custom Keys", add_inbound: "Add Inbound", add_key: "Add Key"
            }
        };"""
content = content.replace(search_transl, replace_transl)

# Update texts to use translation
content = content.replace("Inbounds</a>", "{{ t.inbounds }}</a>")
content = content.replace("Custom Keys</a>", "{{ t.custom_keys }}</a>")
content = content.replace("<h1>Inbounds</h1>", "<h1>{{ t.inbounds }}</h1>")
content = content.replace("<h1>Custom Keys</h1>", "<h1>{{ t.custom_keys }}</h1>")
content = content.replace("Add Inbound</button>", "{{ t.add_inbound }}</button>")
content = content.replace("Add Key</button>", "{{ t.add_key }}</button>")


# 4. Fix sidebar theme consistency
search_sidebar = """<aside v-show="isAuthenticated" class="w-64 bg-slate-900 text-white flex flex-col transition-all duration-300 z-50 border-r border-slate-800" :class="{'hidden sm:flex': !isMobileMenuOpen, 'absolute h-full shadow-2xl': isMobileMenuOpen}">
            <div class="p-6 text-xl font-bold border-b border-slate-800 flex justify-between items-center">"""
replace_sidebar = """<aside v-show="isAuthenticated" class="w-64 bg-white dark:bg-slate-900 text-gray-900 dark:text-white flex flex-col transition-all duration-300 z-50 border-r border-gray-200 dark:border-slate-800" :class="{'hidden sm:flex': !isMobileMenuOpen, 'absolute h-full shadow-2xl': isMobileMenuOpen}">
            <div class="p-6 text-xl font-bold border-b border-gray-200 dark:border-slate-800 flex justify-between items-center">"""
content = content.replace(search_sidebar, replace_sidebar)

# Fix sidebar links to support light mode
content = content.replace(
    """<a href="#" @click="currentTab = 'dashboard'; isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'dashboard'}" class="block p-3 rounded-xl hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-slate-300 hover:text-white">""",
    """<a href="#" @click="currentTab = 'dashboard'; isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'dashboard'}" class="block p-3 rounded-xl hover:bg-blue-600/10 dark:hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-gray-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-white">"""
)
content = content.replace(
    """<a href="#" @click="currentTab = 'users'; isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'users'}" class="block p-3 rounded-xl hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-slate-300 hover:text-white">""",
    """<a href="#" @click="currentTab = 'users'; isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'users'}" class="block p-3 rounded-xl hover:bg-blue-600/10 dark:hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-gray-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-white">"""
)
content = content.replace(
    """<a href="#" @click="currentTab = 'inbounds'; loadInbounds(); isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'inbounds'}" class="block p-3 rounded-xl hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-slate-300 hover:text-white">""",
    """<a href="#" @click="currentTab = 'inbounds'; loadInbounds(); isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'inbounds'}" class="block p-3 rounded-xl hover:bg-blue-600/10 dark:hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-gray-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-white">"""
)
content = content.replace(
    """<a href="#" @click="currentTab = 'custom_keys'; loadCustomKeys(); isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'custom_keys'}" class="block p-3 rounded-xl hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-slate-300 hover:text-white">""",
    """<a href="#" @click="currentTab = 'custom_keys'; loadCustomKeys(); isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'custom_keys'}" class="block p-3 rounded-xl hover:bg-blue-600/10 dark:hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-gray-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-white">"""
)
content = content.replace(
    """<a href="#" @click="currentTab = 'settings'; loadSettings(); isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'settings'}" class="block p-3 rounded-xl hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-slate-300 hover:text-white">""",
    """<a href="#" @click="currentTab = 'settings'; loadSettings(); isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'settings'}" class="block p-3 rounded-xl hover:bg-blue-600/10 dark:hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-gray-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-white">"""
)
content = content.replace(
    """<a href="#" @click="loadLogs(); currentTab = 'logs'; isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'logs'}" class="block p-3 rounded-xl hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-slate-300 hover:text-white">""",
    """<a href="#" @click="loadLogs(); currentTab = 'logs'; isMobileMenuOpen = false" :class="{'bg-blue-600 text-white shadow-md': currentTab === 'logs'}" class="block p-3 rounded-xl hover:bg-blue-600/10 dark:hover:bg-blue-600/50 hover:pl-4 transition-all duration-200 text-gray-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-white">"""
)

# Fix sidebar borders
content = content.replace(
    """<div class="p-4 border-b border-slate-800 flex justify-around items-center bg-slate-800/30">""",
    """<div class="p-4 border-b border-gray-200 dark:border-slate-800 flex justify-around items-center bg-gray-50 dark:bg-slate-800/30">"""
)
content = content.replace(
    """<div class="p-6 border-t border-slate-800 bg-slate-800/30">""",
    """<div class="p-6 border-t border-gray-200 dark:border-slate-800 bg-gray-50 dark:bg-slate-800/30">"""
)


# 5. Add Animations
search_styles = """        .toast-leave-to { opacity: 0; transform: translateY(-30px); }
        [v-cloak] { display: none !important; }
    </style>"""
replace_styles = """        .toast-leave-to { opacity: 0; transform: translateY(-30px); }
        [v-cloak] { display: none !important; }
        .fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
        .fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(10px); }
        .modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
        .modal-enter-active .modal-container, .modal-leave-active .modal-container { transition: transform 0.3s ease; }
        .modal-enter-from, .modal-leave-to { opacity: 0; }
        .modal-enter-from .modal-container, .modal-leave-to .modal-container { transform: scale(0.95) translateY(10px); }
    </style>"""
content = content.replace(search_styles, replace_styles)

# Add transition to Modals
import re

def wrap_modal(modal_id, content):
    pattern_start = re.compile(rf'(<!-- {modal_id} Modal -->\s*<div v-show="{modal_id}ModalOpen" class=")(fixed inset-0[^"]*)(">)')
    match = pattern_start.search(content)
    if not match:
        # try without Modal word
        pattern_start = re.compile(rf'(<!-- {modal_id} -->\s*<div v-show="{modal_id}ModalOpen" class=")(fixed inset-0[^"]*)(">)')
        match = pattern_start.search(content)
    if not match:
        pattern_start = re.compile(rf'(<div v-show="{modal_id}ModalOpen" class=")(fixed inset-0[^"]*)(">)(?!</transition>)')
        match = pattern_start.search(content)

    if match:
        start_idx = match.start()
        # Find closing div
        div_count = 1
        i = match.end()
        while i < len(content) and div_count > 0:
            if content.startswith("<div", i): div_count += 1
            elif content.startswith("</div>", i): div_count -= 1
            if div_count > 0:
                i += 1
            else:
                i += 6 # length of </div>

        modal_content = content[start_idx:i]

        # Add modal-container class to the inner div
        inner_div_pattern = r'(<div class="bg-white dark:bg-slate-900[^"]*)(")'
        modal_content = re.sub(inner_div_pattern, r'\1 modal-container\2', modal_content, count=1)

        wrapped = f'<transition name="modal">\n        {modal_content}\n        </transition>'
        content = content[:start_idx] + wrapped + content[i:]

    return content

content = wrap_modal("isAddUser", content)
content = wrap_modal("isInbound", content)
content = wrap_modal("isCustomKey", content)

# QR Modal is slightly different
pattern_qr = re.compile(r'(<!-- QR Modal -->\s*<div v-show="isQRModalOpen" class=")(fixed inset-0[^"]*)(" @click\.self="isQRModalOpen = false">)')
match_qr = pattern_qr.search(content)
if match_qr:
    start_idx = match_qr.start()
    div_count = 1
    i = match_qr.end()
    while i < len(content) and div_count > 0:
        if content.startswith("<div", i): div_count += 1
        elif content.startswith("</div>", i): div_count -= 1
        if div_count > 0:
            i += 1
        else:
            i += 6

    modal_content = content[start_idx:i]
    modal_content = re.sub(r'(<div class="bg-white dark:bg-slate-900[^"]*)(")', r'\1 modal-container\2', modal_content, count=1)
    wrapped = f'<transition name="modal">\n        {modal_content}\n        </transition>'
    content = content[:start_idx] + wrapped + content[i:]

# Tab content animation
# Replace <div class="p-4 md:p-8 flex-1"> with wrapper
search_main = """            <div class="p-4 md:p-8 flex-1">
                <!-- Dashboard -->"""
replace_main = """            <div class="p-4 md:p-8 flex-1">
                <transition name="fade" mode="out-in">
                    <div :key="currentTab" class="w-full h-full">
                <!-- Dashboard -->"""
content = content.replace(search_main, replace_main)

# And close it right before </main>
search_main_end = """            </div>
        </main>"""
replace_main_end = """                    </div>
                </transition>
            </div>
        </main>"""
content = content.replace(search_main_end, replace_main_end)

with open("recno-master/frontend/index.html", "w") as f:
    f.write(content)
