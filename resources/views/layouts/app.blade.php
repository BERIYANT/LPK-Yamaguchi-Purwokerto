<!DOCTYPE html>
<html lang="id" x-data="{ dark: localStorage.getItem('theme') === 'dark' }" :class="{ 'dark': dark }">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{{ $title ?? 'Dashboard' }} · {{ config('app.name') }}</title>
    <link rel="preconnect" href="https://fonts.bunny.net">
    <link href="https://fonts.bunny.net/css?family=plus-jakarta-sans:400,500,600,700,800&display=swap" rel="stylesheet">
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body x-data="{ sidebarOpen: false }" class="bg-white text-[#20232d] antialiased dark:bg-[#151515] dark:text-[#f5f5f5]">
<div class="min-h-screen lg:flex">
    <div x-show="sidebarOpen" x-transition.opacity class="fixed inset-0 z-40 bg-black/40 lg:hidden" @click="sidebarOpen = false"></div>
    <aside :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'" class="fixed inset-y-0 left-0 z-50 flex w-[270px] flex-col border-r border-[#e9edf2] bg-white text-[#727b8b] transition-transform lg:sticky lg:top-0 lg:h-screen lg:translate-x-0">
        <div class="flex h-20 items-center border-b border-[#edf0f4] px-5">
            <img src="{{ asset('images/logo-yamaguchi.png') }}" alt="Logo LPK Yamaguchi Purwokerto" class="h-14 w-14 rounded-full object-cover">
            <p class="ml-3 text-[15px] font-extrabold leading-tight text-[#20232d]">LPK Yamaguchi<br>Purwokerto</p>
            <button @click="sidebarOpen=false" class="ml-auto text-white/60 lg:hidden" aria-label="Tutup menu">✕</button>
        </div>
        @php
            $icons = [
                'dashboard' => '<svg viewBox="0 0 24 24"><path d="M4 13h6V4H4v9Zm0 7h6v-4H4v4Zm10 0h6v-9h-6v9Zm0-16v4h6V4h-6Z"/></svg>',
                'students' => '<svg viewBox="0 0 24 24"><path d="m3 7 9-4 9 4-9 4-9-4Zm4 3.8V16c3 2.4 7 2.4 10 0v-5.2M21 8v7"/></svg>',
                'teacher' => '<svg viewBox="0 0 24 24"><circle cx="9" cy="7" r="3"/><path d="M3 20c0-5 2-8 6-8s6 3 6 8M16 5h5M18.5 2.5v5"/></svg>',
                'calendar' => '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18M7 14h3M14 14h3M7 18h3"/></svg>',
                'accounts' => '<svg viewBox="0 0 24 24"><circle cx="8" cy="8" r="3"/><path d="M2 20c0-4 2-7 6-7s6 3 6 7M16 11h6M19 8v6"/></svg>',
                'classes' => '<svg viewBox="0 0 24 24"><path d="M4 4h7a2 2 0 0 1 2 2v15a3 3 0 0 0-3-3H4V4Zm16 0h-7v17a3 3 0 0 1 3-3h4V4Z"/></svg>',
                'grades' => '<svg viewBox="0 0 24 24"><path d="M5 3h14v18H5zM8 8h8M8 12h5M8 16h3"/></svg>',
                'activity' => '<svg viewBox="0 0 24 24"><path d="M3 12h4l2-6 4 12 2-6h6"/></svg>',
                'attendance' => '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="m8 12 3 3 5-6"/></svg>',
                'jobs' => '<svg viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V4h8v3M3 12h18"/></svg>',
                'forum' => '<svg viewBox="0 0 24 24"><path d="M4 4h16v13H8l-4 4V4Z"/><path d="M8 9h8M8 13h5"/></svg>',
                'settings' => '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/></svg>',
            ];
            $nav = [
                ['dashboard', 'dashboard', $icons['dashboard'], 'Dashboard', ['admin', 'sensei', 'student']],
                ['participants.*', 'participants.index', $icons['students'], 'Data Siswa', ['admin', 'sensei']],
                ['admin.sensei', 'admin.sensei', $icons['teacher'], 'Data Sensei', ['admin']],
                ['admin.schedules', 'admin.schedules', $icons['calendar'], 'Jadwal Sensei', ['admin']],
                ['admin.accounts', 'admin.accounts', $icons['accounts'], 'Akun E-Learning', ['admin']],
                ['classes.*', 'classes.index', $icons['classes'], 'Kelola Kelas', ['admin', 'sensei', 'student']],
                ['grades.*', 'grades.index', $icons['grades'], 'Penilaian', ['admin', 'sensei']],
                ['admin.activities', 'admin.activities', $icons['activity'], 'Aktivitas', ['admin']],
                ['admin.attendance', 'admin.attendance', $icons['attendance'], 'Absensi', ['admin']],
                ['admin.jobs', 'admin.jobs', $icons['jobs'], 'Lowongan', ['admin']],
                ['admin.forums', 'admin.forums', $icons['forum'], 'Forum', ['admin']],
                ['admin.settings', 'admin.settings', $icons['settings'], 'Pengaturan', ['admin']],
            ];
        @endphp
        <nav class="flex-1 space-y-1 overflow-y-auto px-4 py-5">
            @foreach ($nav as [$pattern, $route, $icon, $label, $roles])
                @if (in_array(Auth::user()->role, $roles, true))
                    <a href="{{ route($route) }}" class="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition {{ request()->routeIs($pattern) ? 'bg-[#fff0f0] text-[#d62828]' : 'text-[#747e8f] hover:bg-[#fff5f5] hover:text-[#d62828]' }}">
                        <span class="flex h-5 w-5 items-center justify-center text-current/85">{!! $icon !!}</span>
                        {{ $label }}
                    </a>
                @endif
            @endforeach
            <div class="my-6 border-t border-white/10"></div>

        </nav>
        <div class="border-t border-[#edf0f4] p-4"><div class="rounded-2xl bg-[#f3f7fa] p-4">
                <div class="flex items-center gap-3">
                    <div class="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-[#ffe8d8] font-extrabold text-[#e2763f]">{{ strtoupper(substr(Auth::user()->name, 0, 1)) }}</div>
                    <div class="min-w-0 flex-1"><p class="truncate text-xs font-bold text-[#20232d]">{{ Auth::user()->name }}</p><p class="mt-0.5 text-[10px] uppercase tracking-wider text-[#929aaa]">{{ Auth::user()->role }}</p></div>
                    <form method="POST" action="{{ route('logout') }}">@csrf<button class="text-[#a7afbc]" title="Keluar">↗</button></form>
                </div>
            </div>
        </div>
    </aside>

    <main class="min-w-0 flex-1">
        <header class="sticky top-0 z-30 flex h-20 items-center border-b border-[#edf0f4] bg-white/95 px-5 backdrop-blur-xl sm:px-8 lg:px-9">
            <button @click="sidebarOpen=true" class="mr-4 grid h-10 w-10 place-items-center rounded-xl border border-black/10 bg-white lg:hidden" aria-label="Buka menu">☰</button>
            <div class="hidden w-full max-w-[480px] items-center gap-3 rounded-full bg-[#fff2f2] px-5 py-3 text-sm text-[#a58f91] sm:flex"><span class="text-[#d62828]">⌕</span><span>Search</span></div>
            <div class="ml-auto flex items-center gap-3">
                <button type="button" @click="dark = !dark; localStorage.setItem('theme', dark ? 'dark' : 'light')" class="grid h-10 w-10 place-items-center rounded-full bg-[#fff0f0] text-[#d62828] dark:bg-[#262626]" :aria-label="dark ? 'Gunakan tema terang' : 'Gunakan tema gelap'" x-text="dark ? '☾' : '☀'"></button>
            </div>
        </header>
        <div class="p-5 sm:p-7 lg:p-8">{{ $slot }}</div>
        {{-- Widget integration slot: place Voiceflow or other approved scripts in a child view. --}}
        @stack('widgets')
    </main>
</div>
</body>
</html>
