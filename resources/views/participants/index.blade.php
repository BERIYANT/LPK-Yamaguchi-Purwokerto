<x-app-layout>
    <x-slot name="pageTitle">Data Siswa</x-slot>
    <div class="mb-7 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
            <p class="eyebrow">Administrasi Akademik</p>
            <h2 class="display-title">Data Siswa</h2>
            <p class="mt-2 text-sm text-black/50">Cari detail berdasarkan NIS atau tampilkan rekap berdasarkan tahun masuk.</p>
        </div>
        <div class="flex flex-wrap gap-2">
            <a href="{{ route('participants.payments') }}" class="rounded-xl border border-[#d62828] px-4 py-3 text-xs font-bold text-[#d62828]">Pembayaran Siswa</a>
            <a href="{{ route('participants.create') }}" class="primary-button">+ Input Siswa</a>
        </div>
    </div>

    <form class="panel mb-5 grid items-end gap-4 md:grid-cols-[minmax(0,1fr)_180px_auto]">
        <label class="min-w-0 text-xs font-bold">NIS / Nama
            <input name="q" value="{{ request('q') }}" class="input mt-2 w-full" placeholder="Contoh: 02240101">
        </label>
        <label class="min-w-0 text-xs font-bold">Tahun masuk
            <select name="year" class="input mt-2 w-full">
                <option value="">Semua tahun</option>
                @foreach($years as $item)
                    <option value="{{ $item }}" @selected((string)request('year') === (string)$item)>{{ $item }}</option>
                @endforeach
            </select>
        </label>
        <button class="primary-button w-full whitespace-nowrap md:w-auto">Tampilkan</button>
    </form>

    @if(session('success'))
        <div class="mb-4 rounded-xl bg-green-50 p-4 text-sm font-bold text-green-700">{{ session('success') }}</div>
    @endif

    <div class="panel overflow-hidden p-0">
        <div class="overflow-x-auto">
            <table class="data-table">
                <thead>
                    <tr>
                        @php
                            $sortField = request('sort', 'name');
                            $sortDir = request('direction', 'asc');
                            $nextDir = $sortDir === 'asc' ? 'desc' : 'asc';
                            $queryParams = request()->except(['sort', 'direction', 'page']);
                        @endphp
                        <th>
                            <a href="{{ route('participants.index', array_merge($queryParams, ['sort' => 'name', 'direction' => $nextDir])) }}" class="flex items-center gap-1 font-bold text-[#20232d] hover:text-[#d62828]">
                                Siswa
                                @if($sortField === 'name')<span>{{ $sortDir === 'asc' ? '↑' : '↓' }}</span>@endif
                            </a>
                        </th>
                        <th>
                            <a href="{{ route('participants.index', array_merge($queryParams, ['sort' => 'nis', 'direction' => $nextDir])) }}" class="flex items-center gap-1 font-bold text-[#20232d] hover:text-[#d62828]">
                                NIS
                                @if($sortField === 'nis')<span>{{ $sortDir === 'asc' ? '↑' : '↓' }}</span>@endif
                            </a>
                        </th>
                        <th>
                            <a href="{{ route('participants.index', array_merge($queryParams, ['sort' => 'enrollment_date', 'direction' => $nextDir])) }}" class="flex items-center gap-1 font-bold text-[#20232d] hover:text-[#d62828]">
                                Tahun
                                @if($sortField === 'enrollment_date')<span>{{ $sortDir === 'asc' ? '↑' : '↓' }}</span>@endif
                            </a>
                        </th>
                        <th>
                            <a href="{{ route('participants.index', array_merge($queryParams, ['sort' => 'school_name', 'direction' => $nextDir])) }}" class="flex items-center gap-1 font-bold text-[#20232d] hover:text-[#d62828]">
                                Asal Sekolah
                                @if($sortField === 'school_name')<span>{{ $sortDir === 'asc' ? '↑' : '↓' }}</span>@endif
                            </a>
                        </th>
                        <th>
                            <a href="{{ route('participants.index', array_merge($queryParams, ['sort' => 'status', 'direction' => $nextDir])) }}" class="flex items-center gap-1 font-bold text-[#20232d] hover:text-[#d62828]">
                                Status
                                @if($sortField === 'status')<span>{{ $sortDir === 'asc' ? '↑' : '↓' }}</span>@endif
                            </a>
                        </th>
                        <th class="w-[120px]"></th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($participants as $participant)
                        @php
                        $statusLabel = ['aktif' => 'Aktif', 'lulus' => 'Lulus', 'keluar' => 'Keluar', 'pending' => 'Tertunda'];
                        $statusColor = ['aktif' => 'text-green-600', 'lulus' => 'text-blue-600', 'keluar' => 'text-red-600', 'pending' => 'text-yellow-600'];
                        $rawStatus = $participant->studentProfile?->status ?: 'aktif';
                        $statusClass = $statusColor[$rawStatus] ?? 'text-gray-600';
                        $statusDisplay = $statusLabel[$rawStatus] ?? ucfirst($rawStatus);
                    @endphp
                        <tr>
                            <td>
                                <div class="flex items-center gap-3">
                                    <div class="avatar">{{ strtoupper(substr($participant->name,0,1)) }}</div>
                                    <div>
                                        <b>{{ $participant->name }}</b>
                                        <small>{{ $participant->phone ?: 'Tanpa nomor WA' }}</small>
                                    </div>
                                </div>
                            </td>
                            <td>{{ $participant->studentProfile?->nis ?? '—' }}</td>
                            <td>{{ $participant->studentProfile?->enrollment_date ? \Illuminate\Support\Carbon::parse($participant->studentProfile->enrollment_date)->year : '—' }}</td>
                            <td>{{ $participant->studentProfile?->school_name ?? '—' }}</td>
                            <td><span class="status-pill {{ $statusClass }}">{{ $statusDisplay }}</span></td>
                            <td>
                                <div class="flex gap-2">
                                    @if($participant->studentProfile?->nis)
                                        <a class="font-bold text-[#d62828]" href="{{ route('participants.edit', ['nis' => $participant->studentProfile->nis]) }}" title="Edit">✎</a>
                                        <a class="font-bold text-[#d62828]" href="{{ route('participants.show', ['nis' => $participant->studentProfile->nis]) }}" title="Detail">→</a>
                                    @else
                                        <span class="text-xs text-black/35">Profil belum lengkap</span>
                                    @endif
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="6" class="empty-state">Data siswa tidak ditemukan.</td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        <div class="border-t border-black/[.06] p-5">{{ $participants->links() }}</div>
    </div>
</x-app-layout>
