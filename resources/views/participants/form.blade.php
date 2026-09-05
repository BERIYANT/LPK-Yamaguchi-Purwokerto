<x-app-layout>
    <x-slot name="pageTitle">{{ $participant ? 'Edit Data Siswa' : 'Input Data Siswa' }}</x-slot>

    <div class="mb-7 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
            <p class="eyebrow">Data Siswa</p>
            <h2 class="display-title">{{ $participant ? 'Edit data siswa.' : 'Input data siswa.' }}</h2>
        </div>
        @if($participant)
            <a href="{{ route('participants.show', ['nis' => $participant->studentProfile->nis]) }}" class="text-sm font-bold text-[#d62828]">← Kembali ke Detail</a>
        @else
            <a href="{{ route('participants.index') }}" class="text-sm font-bold text-[#d62828]">← Kembali ke Data Siswa</a>
        @endif
    </div>

    @php
        $p = $participant ?? null;
        $profile = $p ? $p->studentProfile : null;
        $fields = [
            ['nis', 'NIS', 'text', true, false],
            ['full_name', 'Nama lengkap', 'text', true, true],
            ['gender', 'Jenis kelamin', 'select', false, true],
            ['birth_place', 'Tempat lahir', 'text', false, true],
            ['birth_date', 'Tanggal lahir', 'date', false, true],
            ['school_name', 'Asal sekolah', 'text', false, true],
            ['nik', 'NIK', 'text', false, true],
            ['phone', 'Nomor WA', 'text', false, true],
            ['address', 'Alamat', 'text', false, true],
            ['rt_rw', 'RT/RW', 'text', false, true],
            ['village', 'Desa/Kelurahan', 'text', false, true],
            ['district', 'Kecamatan', 'text', false, true],
            ['city', 'Kabupaten/Kota', 'text', false, true],
            ['province', 'Provinsi', 'text', false, true],
            ['enrollment_date', 'Tanggal masuk', 'date', true, true],
            ['graduation_date', 'Tanggal lulus', 'date', false, true],
            ['departure_date', 'Tanggal terbang', 'date', false, true],
            ['job_sector', 'Sektor pekerjaan', 'text', false, true],
            ['placement', 'Penempatan', 'text', false, true],
            ['status', 'Status', 'status', false, true],
            ['notes', 'Catatan', 'text', false, true],
        ];
    @endphp

    <form method="POST" action="{{ $p ? route('participants.update', ['nis' => $profile->nis]) : route('participants.store') }}" class="panel">
        @csrf
        @if($p) @method('PUT') @endif

        @if($errors->any())
            <div class="mb-5 rounded-xl bg-red-50 p-4 text-sm text-red-700">{{ $errors->first() }}</div>
        @endif

        <div class="grid gap-5 md:grid-cols-2">
            @foreach($fields as [$name, $label, $type, $required, $editable])
                @php
                    $value = $profile?->{$name} ?? old($name);
                @endphp
                <label class="text-xs font-bold">{{ $label }}@if($required)<span class="text-red-600"> *</span>@endif
                    @if($type === 'select' && $name === 'gender')
                        <select name="{{ $name }}" class="input mt-2 w-full" @disabled(!$editable)>
                            <option value="">Pilih</option>
                            <option value="L" @selected(($value ?? '') === 'L')>Laki-laki</option>
                            <option value="P" @selected(($value ?? '') === 'P')>Perempuan</option>
                        </select>
                    @elseif($type === 'status')
                        <select name="{{ $name }}" class="input mt-2 w-full" @required($required)>
                            <option value="aktif" @selected(($value ?? 'aktif') === 'aktif')>Aktif</option>
                            <option value="lulus" @selected(($value ?? '') === 'lulus')>Lulus</option>
                            <option value="keluar" @selected(($value ?? '') === 'keluar')>Keluar</option>
                            <option value="pending" @selected(($value ?? '') === 'pending')>Tertunda</option>
                        </select>
                    @elseif($name === 'nis')
                        @if($p)
                            <input type="text" value="{{ $value }}" class="input mt-2 w-full" readonly>
                        @else
                            <input name="{{ $name }}" type="text" value="{{ old($name) }}" class="input mt-2 w-full" @required($required)>
                        @endif
                    @else
                        <input name="{{ $name }}" type="{{ $type }}" value="{{ $value }}" class="input mt-2 w-full" @required($required)>
                    @endif
                </label>
            @endforeach
        </div>

        <div class="mt-6 flex gap-3">
            <button class="primary-button">{{ $p ? 'Simpan Perubahan' : 'Simpan Siswa' }}</button>
            <a href="{{ $p ? route('participants.show', ['nis' => $profile->nis]) : route('participants.index') }}" class="rounded-xl border px-5 py-3 text-xs font-bold">Batal</a>
        </div>
    </form>
</x-app-layout>
