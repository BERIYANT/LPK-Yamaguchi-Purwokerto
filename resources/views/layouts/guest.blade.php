<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ config('app.name', 'Laravel') }}</title>

        <!-- Fonts -->
        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=figtree:400,500,600&display=swap" rel="stylesheet" />

        <!-- Scripts -->
        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="font-sans text-[#0b1f3a] antialiased">
        <div class="relative min-h-screen flex flex-col sm:justify-center items-center px-5 py-8 bg-[#f4f7fb] overflow-hidden">
            <div class="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-[#d62828]/10"></div>
            <div class="absolute -bottom-32 -left-24 h-80 w-80 rounded-full bg-[#0b1f3a]/10"></div>
            <div class="relative text-center">
                <a href="/" class="inline-flex"><img src="{{ asset('images/logo-yamaguchi.png') }}" alt="Logo LPK Yamaguchi Purwokerto" class="h-24 w-24 rounded-full object-cover"></a>
                <h1 class="mt-4 text-xl font-extrabold tracking-[-.02em] text-[#202020]">LPK Yamaguchi Purwokerto</h1>
                <p class="mt-1 text-xs font-semibold uppercase tracking-[.18em] text-black/40">Sistem Administrasi & E-Learning</p>
            </div>

            <div class="relative w-full sm:max-w-md mt-8 px-7 py-8 bg-white border border-[#0b1f3a]/10 shadow-[0_24px_70px_rgba(11,31,58,.12)] overflow-hidden rounded-3xl">
                {{ $slot }}
            </div>
        </div>
    </body>
</html>
