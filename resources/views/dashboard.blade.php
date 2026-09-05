<x-app-layout>
    <x-slot name="pageTitle">Dashboard</x-slot>

    @if(Auth::user()->role === 'admin')
        @php
            $cards = [
                ['Total Siswa', $metrics['participants'], '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="7" r="3"/><path d="M5 20v-2a7 7 0 0 1 14 0v2"/></svg>', '#d62828', 'from-[#fffafa] to-[#fff0f0]'],
                ['Total Sensei', $metrics['sensei'], '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="7" r="3"/><path d="M6 20c.4-4 2.5-6 6-6s5.6 2 6 6M16 4l2-2m0 0v3m0-3h-3"/></svg>', '#e13b32', 'from-[#fff9f9] to-[#ffeaea]'],
                ['Total Kelas', $metrics['classes'], '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22zM20 5.5A2.5 2.5 0 0 0 17.5 3H13v17h4.5a2.5 2.5 0 0 1 2.5 2z"/></svg>', '#bd1f27', 'from-[#fff7f7] to-[#ffe5e5]'],
                ['Total Modul', $metrics['materials'], '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>', '#ef5147', 'from-[#fffafa] to-[#ffeded]'],
                ['Total Tugas', $metrics['tasks'], '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m5 12 4 4L19 6"/></svg>', '#d62828', 'from-[#fff8f8] to-[#ffe7e7]'],
                ['Perlu Dinilai', $metrics['pendingGrades'], '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="8" y="8" width="8" height="8" rx="1"/></svg>', '#a91820', 'from-[#fff7f7] to-[#ffe3e3]'],
            ];
            $months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
        @endphp

        <section class="mb-8">
            <h2 class="text-3xl font-extrabold tracking-[-.04em] text-[#172033] sm:text-4xl">Dashboard</h2>
            <p class="mt-3 text-sm font-medium text-[#788399]">Sekolah <span class="mx-2 text-[#aab2c0]">→</span> Kelola siswa, kelas, kehadiran, dan aktivitas akademik.</p>
        </section>

        <section class="grid items-stretch gap-6 xl:grid-cols-[minmax(0,2.15fr)_minmax(310px,.85fr)]">
            <div class="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                @foreach($cards as [$label, $value, $icon, $color, $gradient])
                    <article class="admin-stat-card bg-gradient-to-br {{ $gradient }}">
                        <div class="admin-stat-icon" style="background: {{ $color }}">{!! $icon !!}</div>
                        <div>
                            <p>{{ $label }}</p>
                            <strong>{{ number_format($value) }}</strong>
                            <span><b class="!text-[#d62828]">10% ▲</b> &nbsp; +5 Bulan Ini</span>
                        </div>
                    </article>
                @endforeach
            </div>

            <article class="admin-panel flex flex-col">
                <div class="admin-panel-title"><h3>Student Attendance</h3></div>
                <div class="flex flex-1 flex-col p-6">
                    <div class="flex h-3 overflow-hidden rounded-full bg-[#edf1f6]">
                        @foreach($attendance as $item)
                            @if($item['percentage'] > 0)<span style="width: {{ $item['percentage'] }}%; background: {{ $item['color'] }}"></span>@endif
                        @endforeach
                    </div>
                    <div class="mt-8 space-y-5">
                        @foreach($attendance as $item)
                            <div class="flex items-center gap-3 text-sm"><span class="h-3 w-3 rounded-[3px]" style="background: {{ $item['color'] }}"></span><span class="font-semibold text-[#6e7788]">{{ $item['label'] }}</span><b class="ml-auto text-[#20283a]">{{ $item['percentage'] }}%</b></div>
                        @endforeach
                    </div>

                </div>
            </article>
        </section>

        <section class="mt-6 grid gap-6 xl:grid-cols-[minmax(0,2.15fr)_minmax(310px,.85fr)]">
            <section>
                <h3 class="mb-4 text-lg font-extrabold text-[#20232d]">Rincian Siswa</h3>
                <div class="grid gap-4 sm:grid-cols-2">
                    <article class="admin-stat-card bg-gradient-to-br from-[#fffafa] to-[#fff0f0]">
                        <div class="admin-stat-icon" style="background: #d62828">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="7" r="3"/><path d="M5 20v-2a7 7 0 0 1 14 0v2"/></svg>
                        </div>
                        <div>
                            <p>Total Siswa</p>
                            <strong>{{ number_format($studentStats['total']) }}</strong>
                            <span>Data database aktif</span>
                        </div>
                    </article>
                    <article class="admin-stat-card bg-gradient-to-br from-[#eef7ff] to-[#f0f9ff]">
                        <div class="admin-stat-icon" style="background: #3b82f6">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="8" cy="7" r="3"/><path d="M2 20c0-4 2-7 6-7s6 3 6 7M16 5h5a2 2 0 0 1 2 2v3m-2 7a4 4 0 1 0-8 0"/></svg>
                        </div>
                        <div>
                            <p>Siswa Aktif</p>
                            <strong class="text-[#3b82f6]">{{ number_format($studentStats['status']['aktif'] ?? 0) }}</strong>
                            <span>{{ number_format($studentStats['status']['lulus'] ?? 0) }} Lulus · {{ number_format($studentStats['status']['keluar'] ?? 0) }} Keluar</span>
                        </div>
                    </article>
                </div>

                <div class="mt-4 grid gap-4 sm:grid-cols-2">
                    <article class="panel">
                        <div class="panel-head"><h3>Gender Siswa</h3></div>
                        <div class="space-y-3">
                            <div class="flex items-center gap-3">
                                <span class="w-32 font-semibold text-[#6e7788]">Laki-laki</span>
                                <div class="flex-1 h-5 overflow-hidden rounded-full bg-[#edf1f6]">
                                    <span class="flex h-full w-1/2 min-w-[2px] items-center justify-center rounded-full bg-[#d62828] text-[10px] font-black text-white" style="width: {{ ($studentStats['gender']['L'] ?? 0) + ($studentStats['gender']['P'] ?? 1) > 0 ? (($studentStats['gender']['L'] ?? 0) / (($studentStats['gender']['L'] ?? 0) + ($studentStats['gender']['P'] ?? 1)) * 100) : 0 }}%">
                                        {{ number_format($studentStats['gender']['L'] ?? 0) }}
                                    </span>
                                </div>
                            </div>
                            <div class="flex items-center gap-3">
                                <span class="w-32 font-semibold text-[#6e7788]">Perempuan</span>
                                <div class="flex-1 h-5 overflow-hidden rounded-full bg-[#edf1f6]">
                                    <span class="flex h-full min-w-[2px] items-center justify-center rounded-full bg-[#bd1f27] text-[10px] font-black text-white" style="width: {{ ($studentStats['gender']['L'] ?? 0) + ($studentStats['gender']['P'] ?? 1) > 0 ? (($studentStats['gender']['P'] ?? 0) / (($studentStats['gender']['L'] ?? 0) + ($studentStats['gender']['P'] ?? 1)) * 100) : 0 }}%">
                                        {{ number_format($studentStats['gender']['P'] ?? 0) }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </article>

                    <article class="panel">
                        <div class="panel-head"><h3>Status Siswa</h3></div>
                        <div class="space-y-3">
                            @foreach([
                                ['aktif', 'Aktif', '#16a34a'],
                                ['lulus', 'Lulus', '#3b82f6'],
                                ['keluar', 'Keluar', '#dc2626'],
                                ['pending', 'Tertunda', '#eab308'],
                            ] as [$key, $label, $color])
                                <div class="flex items-center justify-between">
                                    <span class="font-semibold text-[#6e7788]">{{ $label }}</span>
                                    <strong style="color: {{ $color }}">{{ number_format($studentStats['status'][$key] ?? 0) }}</strong>
                                </div>
                            @endforeach
                        </div>
                    </article>
                </div>
            </section>

            <article class="admin-panel">
                <div class="admin-panel-title"><h3>Distribusi ke Jepang</h3></div>
                <div class="p-6">
                    <div class="space-y-4">
                        @foreach($studentStats['cities'] as $city => $count)
                            <div class="flex items-center gap-3">
                                <span class="min-w-[80px] text-sm font-bold text-[#6e7788]">{{ $city }}</span>
                                <div class="relative flex-1 h-8">
                                    <div class="absolute inset-0 flex items-center rounded-xl bg-[#edf1f6]">
                                        <span class="ml-3 text-xs font-black text-[#20232d]">{{ number_format($count) }} siswa</span>
                                    </div>
                                    <div class="h-full rounded-xl bg-[#d62828]" style="width: {{ ($count / max(1, $studentStats['cities']->max())) * 100 }}%"></div>
                                </div>
                            </div>
                        @endforeach
                    </div>
                </div>
            </article>
        </section>
            <article class="admin-panel">
                <div class="admin-panel-title"><h3>Revenue Statistic</h3></div>
                <div class="p-6 sm:p-8">
                    <div class="mb-8 flex flex-wrap justify-center gap-6 text-xs font-semibold text-[#7c8799]"><span><i class="mr-2 inline-block h-2.5 w-2.5 rotate-45 bg-[#a91820]"></i>Siswa Baru: <b class="text-[#a91820]">{{ $monthlyStudents->sum() }}</b></span><span><i class="mr-2 inline-block h-2.5 w-2.5 rotate-45 bg-[#ef5147]"></i>Tugas & Kuis: <b class="text-[#d62828]">{{ $monthlyAcademic->sum() }}</b></span></div>
                    <div class="chart-grid">
                        @foreach($months as $index => $month)
                            @php $studentHeight = max(0, round(($monthlyStudents[$index] / $chartMaximum) * 100)); $academicHeight = max(0, round(($monthlyAcademic[$index] / $chartMaximum) * 100)); @endphp
                            <div class="chart-column">
                                <div class="chart-bars"><span class="bg-[#a91820]" style="height: {{ $studentHeight }}%" title="{{ $monthlyStudents[$index] }} siswa"></span><span class="bg-[#ef5147]" style="height: {{ $academicHeight }}%" title="{{ $monthlyAcademic[$index] }} aktivitas"></span></div>
                                <small>{{ $month }}</small>
                            </div>
                        @endforeach
                    </div>
                </div>
            </article>

            <article class="admin-panel">
                <div class="admin-panel-title"><h3>Calendar</h3></div>
                <div class="p-5 sm:p-6">
                    <div class="flex items-center justify-between rounded-2xl bg-[#eaf0f7] p-2.5 text-[#0b1f3a]"><a class="calendar-arrow" href="?year={{ $previousMonth->year }}&month={{ $previousMonth->month }}">‹</a><b class="text-sm text-[#0b1f3a]">{{ $calendarDate->translatedFormat('F Y') }}</b><a class="calendar-arrow" href="?year={{ $nextMonth->year }}&month={{ $nextMonth->month }}">›</a></div>
                    <div class="mt-6 grid grid-cols-7 gap-y-3 text-center text-xs font-bold text-[#233047]">@foreach(['Min','Sen','Sel','Rab','Kam','Jum','Sab'] as $day)<span>{{ $day }}</span>@endforeach</div>
                    <div class="mt-4 grid grid-cols-7 gap-y-2 text-center text-sm text-[#687386]">
                        @foreach($calendarDays as $day)
                            <span class="grid h-9 place-items-center rounded-xl {{ $day && $calendarDate->year === now()->year && $calendarDate->month === now()->month && $day === now()->day ? 'bg-[#d62828] font-extrabold text-white shadow-lg shadow-red-200' : '' }}">{{ $day }}</span>
                        @endforeach
                    </div>
                </div>
            </article>
        </section>
    @else
        <section class="mb-8"><p class="eyebrow">Pusat Aktivitas</p><h2 class="display-title">Selamat datang, {{ explode(' ', Auth::user()->name)[0] }}.</h2><p class="mt-2 text-sm text-black/50">Pantau kelas dan kegiatan belajar Anda.</p></section>
        <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">@foreach ([['Peserta Aktif', $metrics['participants'], '◎', 'red'], ['Kelas Berjalan', $metrics['classes'], '▤', 'black'], ['Modul Belajar', $metrics['materials'], '▱', 'cream'], ['Perlu Dinilai', $metrics['pendingGrades'], '✓', 'yellow']] as [$label, $value, $icon, $tone])<article class="metric-card tone-{{ $tone }}"><div class="metric-icon">{{ $icon }}</div><p>{{ $label }}</p><strong>{{ number_format($value) }}</strong><span>Data database aktif</span></article>@endforeach</section>
    @endif
</x-app-layout>
