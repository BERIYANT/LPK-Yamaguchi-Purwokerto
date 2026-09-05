<!DOCTYPE html>
<html lang="id" class="scroll-smooth">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Pelatihan bahasa, budaya, dan kesiapan kerja ke Jepang bersama LPK Yamaguchi Purwokerto.">
    <title>LPK Yamaguchi Purwokerto</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="bg-white text-[#0b1f3a] antialiased selection:bg-[#d62828] selection:text-white">
    <div class="overflow-hidden">
        <header class="relative z-30 mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
            <a href="{{ route('home') }}" class="group flex items-center" aria-label="Halaman awal LPK Yamaguchi">
                <img src="{{ asset('images/logo-yamaguchi.png') }}" alt="Logo LPK Yamaguchi Purwokerto" class="h-16 w-16 rounded-full object-cover">
                <span class="ml-3">
                    <strong class="block text-sm font-black tracking-[-.02em]">LPK YAMAGUCHI</strong>
                    <small class="block text-[9px] font-extrabold uppercase tracking-[.24em] text-black/40">Purwokerto</small>
                </span>
            </a>

            <nav class="hidden items-center gap-8 text-xs font-extrabold md:flex" aria-label="Navigasi utama">
                <a href="#program" class="transition hover:text-[#cf3028]">Program</a>
                <a href="#keunggulan" class="transition hover:text-[#cf3028]">Keunggulan</a>
                <a href="#alur" class="transition hover:text-[#cf3028]">Alur Belajar</a>
            </nav>

            @auth
                <a href="{{ route('dashboard') }}" class="rounded-full bg-[#0b1f3a] px-5 py-3 text-xs font-extrabold text-white transition hover:-translate-y-0.5 hover:bg-[#d62828]">Dashboard <span class="ml-2">→</span></a>
            @else
                <a href="{{ route('login') }}" class="rounded-full bg-[#0b1f3a] px-5 py-3 text-xs font-extrabold text-white transition hover:-translate-y-0.5 hover:bg-[#d62828]">Masuk <span class="ml-2">→</span></a>
            @endauth
        </header>

        <main>
            <section class="relative mx-auto grid min-h-[720px] w-full max-w-7xl items-center gap-12 px-6 pb-20 pt-10 lg:grid-cols-[1.08fr_.92fr] lg:px-10 lg:pb-28 lg:pt-16">
                <div class="pointer-events-none absolute -left-40 top-20 h-80 w-80 rounded-full bg-[#cf3028]/10 blur-3xl"></div>
                <div class="relative z-10">
                    <div class="inline-flex items-center gap-3 rounded-full border border-black/10 bg-white/50 px-4 py-2 backdrop-blur">
                        <span class="h-2 w-2 rounded-full bg-[#cf3028]"></span>
                        <p class="text-[10px] font-black uppercase tracking-[.2em]">Pelatihan Kerja ke Jepang</p>
                    </div>
                    <h1 class="mt-7 max-w-3xl text-5xl font-black leading-[.92] tracking-[-.065em] sm:text-7xl lg:text-[88px]">
                        Mimpi besar,<br><span class="text-[#cf3028]">langkah nyata.</span>
                    </h1>
                    <p class="mt-7 max-w-xl text-base font-medium leading-8 text-black/55 sm:text-lg">
                        Kuasai bahasa, pahami budaya, dan bangun kesiapan kerja untuk memulai masa depanmu di Jepang.
                    </p>
                    <div class="mt-9 flex flex-wrap items-center gap-4">
                        @auth
                            <a href="{{ route('dashboard') }}" class="group inline-flex items-center gap-4 rounded-2xl bg-[#cf3028] px-6 py-4 text-sm font-black text-white shadow-xl shadow-red-900/20 transition hover:-translate-y-1 hover:bg-[#b92721]">Buka Dashboard <span class="transition group-hover:translate-x-1">→</span></a>
                        @else
                            <a href="{{ route('login') }}" class="group inline-flex items-center gap-4 rounded-2xl bg-[#cf3028] px-6 py-4 text-sm font-black text-white shadow-xl shadow-red-900/20 transition hover:-translate-y-1 hover:bg-[#b92721]">Mulai Perjalanan <span class="transition group-hover:translate-x-1">→</span></a>
                        @endauth
                        <a href="#program" class="inline-flex items-center gap-2 px-3 py-4 text-sm font-black transition hover:text-[#cf3028]"><span class="grid h-8 w-8 place-items-center rounded-full border border-black/15">↓</span> Jelajahi Program</a>
                    </div>
                    <div class="mt-12 flex flex-wrap gap-x-10 gap-y-5 border-t border-black/10 pt-7">
                        <div><strong class="text-2xl font-black">3</strong><span class="ml-2 text-xs font-bold text-black/45">Tahap pelatihan</span></div>
                        <div><strong class="text-2xl font-black">N5–N3</strong><span class="ml-2 text-xs font-bold text-black/45">Target bahasa</span></div>
                        <div><strong class="text-2xl font-black">360°</strong><span class="ml-2 text-xs font-bold text-black/45">Pendampingan</span></div>
                    </div>
                </div>

                <div class="relative mx-auto w-full max-w-[520px]">
                    <div class="absolute -right-16 -top-12 h-52 w-52 rounded-full border-[42px] border-[#0b1f3a]/10"></div>
                    <div class="relative rotate-2 rounded-[40px] bg-[#0b1f3a] p-3 shadow-[0_40px_90px_rgba(11,31,58,.24)] transition duration-500 hover:rotate-0">
                        <div class="relative min-h-[540px] overflow-hidden rounded-[31px] bg-[#d62828] p-8 text-white sm:p-10">
                            <div class="absolute -right-28 -top-24 h-80 w-80 rounded-full border-[70px] border-white/10"></div>
                            <div class="absolute -bottom-28 -left-20 h-64 w-64 rounded-full border-[50px] border-[#0b1f3a]/25"></div>
                            <div class="relative flex items-start justify-between">
                                <p class="text-[10px] font-black uppercase tracking-[.25em] text-white/70">Yamaguchi Method</p>
                                <span class="grid h-12 w-12 place-items-center rounded-full bg-white text-xl font-black text-[#cf3028]">日</span>
                            </div>
                            <div class="relative mt-24">
                                <p class="font-serif text-7xl leading-none text-white/20">日本</p>
                                <h2 class="mt-5 text-4xl font-black leading-[1.02] tracking-[-.045em] sm:text-5xl">Bukan sekadar belajar bahasa.</h2>
                                <p class="mt-6 max-w-sm text-sm font-semibold leading-7 text-white/70">Kami membentuk disiplin, mental, dan keterampilan yang dibutuhkan untuk hidup serta bekerja di Jepang.</p>
                            </div>
                            <div class="relative mt-14 flex items-center justify-between border-t border-white/20 pt-6">
                                <span class="text-xs font-black">PURWOKERTO — JEPANG</span>
                                <span class="text-2xl">↗</span>
                            </div>
                        </div>
                    </div>
                    <div class="absolute -bottom-7 left-5 z-20 rounded-2xl bg-white px-5 py-4 text-[#0b1f3a] shadow-xl ring-1 ring-[#0b1f3a]/10 sm:-left-7">
                        <p class="text-[9px] font-black uppercase tracking-[.18em] text-black/50">Fokus Kami</p>
                        <p class="mt-1 text-sm font-black">Siap bahasa · Siap kerja</p>
                    </div>
                </div>
            </section>

            <section id="program" class="bg-[#0b1f3a] py-24 text-white">
                <div class="mx-auto max-w-7xl px-6 lg:px-10">
                    <div class="grid gap-8 lg:grid-cols-[.75fr_1.25fr] lg:items-end">
                        <div>
                            <p class="text-[10px] font-black uppercase tracking-[.24em] text-[#ef6a5f]">Program Pembelajaran</p>
                            <h2 class="mt-4 text-4xl font-black tracking-[-.05em] sm:text-5xl">Satu jalur.<br>Tiga bekal utama.</h2>
                        </div>
                        <p class="max-w-xl text-sm font-medium leading-7 text-white/65 lg:justify-self-end">Kurikulum praktis yang dirancang untuk membangun kemampuan secara bertahap—dari komunikasi sehari-hari hingga kesiapan menghadapi lingkungan kerja Jepang.</p>
                    </div>
                    <div class="mt-14 grid gap-4 md:grid-cols-3">
                        @foreach ([
                            ['01', 'Bahasa Jepang', 'Komunikasi aktif, tata bahasa, kanji, dan persiapan ujian kemampuan bahasa.'],
                            ['02', 'Budaya & Disiplin', 'Memahami etos kerja, kebiasaan, tata krama, serta kehidupan sehari-hari di Jepang.'],
                            ['03', 'Kesiapan Kerja', 'Simulasi wawancara, penguatan mental, administrasi, dan pendampingan keberangkatan.'],
                        ] as [$number, $title, $description])
                            <article class="group rounded-[28px] border border-white/10 bg-white/[.04] p-7 transition duration-300 hover:-translate-y-2 hover:border-[#ef6a5f]/60 hover:bg-white/[.07]">
                                <div class="flex items-center justify-between"><span class="text-xs font-black text-[#ef6a5f]">{{ $number }}</span><span class="h-px w-10 bg-white/20 transition group-hover:w-14 group-hover:bg-[#ef6a5f]"></span></div>
                                <h3 class="mt-16 text-2xl font-black tracking-[-.03em]">{{ $title }}</h3>
                                <p class="mt-4 text-sm font-medium leading-7 text-white/65">{{ $description }}</p>
                            </article>
                        @endforeach
                    </div>
                </div>
            </section>

            <section id="keunggulan" class="py-24">
                <div class="mx-auto grid max-w-7xl gap-14 px-6 lg:grid-cols-2 lg:px-10">
                    <div class="rounded-[36px] bg-[#eef3f9] p-8 ring-1 ring-[#0b1f3a]/10 sm:p-12">
                        <p class="text-[10px] font-black uppercase tracking-[.24em] text-[#a72d25]">Mengapa Yamaguchi?</p>
                        <h2 class="mt-4 text-4xl font-black tracking-[-.05em]">Belajar dengan arah yang jelas.</h2>
                        <p class="mt-6 max-w-lg text-sm font-semibold leading-7 text-black/50">Setiap tahap dipantau melalui platform terpadu agar peserta, sensei, dan pengelola selalu terhubung dengan perkembangan belajar.</p>
                        <div class="mt-10 grid grid-cols-2 gap-3">
                            <div class="rounded-2xl bg-white/60 p-5"><strong class="text-3xl font-black text-[#cf3028]">01</strong><p class="mt-3 text-xs font-black">Pembelajaran terukur</p></div>
                            <div class="rounded-2xl bg-white/60 p-5"><strong class="text-3xl font-black text-[#cf3028]">02</strong><p class="mt-3 text-xs font-black">Sensei berpengalaman</p></div>
                        </div>
                    </div>
                    <div id="alur" class="flex flex-col justify-center">
                        <p class="text-[10px] font-black uppercase tracking-[.24em] text-[#cf3028]">Alur Belajar</p>
                        <div class="mt-7 space-y-2">
                            @foreach ([['Kenali kemampuanmu', 'Pemetaan awal dan target belajar personal.'], ['Bangun fondasi', 'Bahasa, budaya, disiplin, dan kebiasaan kerja.'], ['Siapkan keberangkatan', 'Pendampingan hingga siap memasuki dunia kerja.']] as $index => [$title, $description])
                                <div class="group flex gap-5 rounded-2xl border border-transparent p-5 transition hover:border-black/10 hover:bg-white/60">
                                    <span class="grid h-10 w-10 shrink-0 place-items-center rounded-full border border-black/15 text-xs font-black transition group-hover:border-[#cf3028] group-hover:bg-[#cf3028] group-hover:text-white">{{ $index + 1 }}</span>
                                    <div><h3 class="text-lg font-black">{{ $title }}</h3><p class="mt-1 text-sm font-medium leading-6 text-black/45">{{ $description }}</p></div>
                                </div>
                            @endforeach
                        </div>
                    </div>
                </div>
            </section>

            <section class="mx-auto max-w-7xl px-6 pb-10 lg:px-10">
                <div class="relative overflow-hidden rounded-[36px] bg-[#cf3028] px-7 py-14 text-center text-white sm:px-12 sm:py-20">
                    <div class="absolute -left-20 -top-28 h-72 w-72 rounded-full border-[60px] border-white/10"></div>
                    <div class="relative">
                        <p class="text-[10px] font-black uppercase tracking-[.24em] text-white/60">Mulai Hari Ini</p>
                        <h2 class="mx-auto mt-4 max-w-3xl text-4xl font-black tracking-[-.05em] sm:text-6xl">Masa depanmu tidak perlu menunggu.</h2>
                        @auth
                            <a href="{{ route('dashboard') }}" class="mt-9 inline-flex rounded-2xl bg-white px-7 py-4 text-sm font-black text-[#cf3028] transition hover:-translate-y-1">Buka Dashboard →</a>
                        @else
                            <a href="{{ route('login') }}" class="mt-9 inline-flex rounded-2xl bg-white px-7 py-4 text-sm font-black text-[#cf3028] transition hover:-translate-y-1">Mulai Sekarang →</a>
                        @endauth
                    </div>
                </div>
            </section>
        </main>

        <footer class="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-10 text-xs font-bold text-black/55 sm:flex-row sm:items-center sm:justify-between lg:px-10">
            <p>© {{ date('Y') }} LPK Yamaguchi Purwokerto</p>
            <p>Belajar · Berkembang · Berkarier</p>
        </footer>
    </div>
</body>
</html>