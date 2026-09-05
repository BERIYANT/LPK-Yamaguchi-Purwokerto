<?php

namespace App\Http\Controllers;

use App\Models\AttendanceSession;
use App\Models\ForumPost;
use App\Models\Job;
use App\Models\SenseiProfile;
use App\Models\TeachingSchedule;
use App\Models\User;
use Illuminate\View\View;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;

class AdministrationController extends Controller
{
    public function sensei(): View
    {
        return view('administration.sensei', ['sensei' => User::with('senseiProfile')->where('role', 'sensei')->orderBy('full_name')->get()]);
    }

    public function storeSensei(Request $request): RedirectResponse
    {
        $data = $request->validate([
            'sensei_code' => ['required', 'string', 'max:30', 'unique:sensei_profiles,sensei_code'],
            'full_name' => ['required', 'string', 'max:255'],
            'username' => ['required', 'string', 'max:100', 'unique:users,username'],
            'phone' => ['nullable', 'string', 'max:30'],
            'address' => ['nullable', 'string'],
            'teaching_field' => ['nullable', 'string', 'max:100'],
            'status' => ['required', 'in:aktif,nonaktif'],
        ]);
        $user = User::create(['username' => $data['username'], 'full_name' => $data['full_name'], 'phone' => $data['phone'] ?? null, 'role' => 'sensei', 'password' => Hash::make(str()->random(24)), 'registration_completed' => 1]);
        $user->senseiProfile()->create($data);

        return redirect()->route('admin.sensei')->with('success', 'Data sensei berhasil ditambahkan.');
    }

    public function schedules(): View
    {
        return $this->listing('Jadwal Sensei', 'Jadwal Mengajar', ['Tanggal', 'Sensei', 'Kelas', 'Materi', 'Waktu'],
            TeachingSchedule::with('sensei')->orderByDesc('teaching_date')->get()->map(fn ($item) => [$item->teaching_date, $item->sensei?->full_name ?? '—', $item->class_name, $item->subject, substr($item->start_time, 0, 5).'–'.substr($item->end_time, 0, 5)]));
    }

    public function accounts(): View
    {
        return $this->listing('Akun E-Learning', 'Manajemen Akses', ['Nama', 'Username', 'Email', 'Role', 'Terdaftar'],
            User::orderBy('role')->orderBy('full_name')->get()->map(fn ($item) => [$item->name, $item->username ?: '—', $item->email ?: '—', $item->role ?: '—', $item->created_at ?: '—']));
    }

    public function attendance(): View
    {
        return $this->listing('Absensi', 'Sesi Kehadiran', ['Tanggal', 'Kelas', 'Pengajar', 'Keterangan', 'Status'],
            AttendanceSession::with(['lmsClass', 'teacher'])->orderByDesc('date')->get()->map(fn ($item) => [$item->date, $item->lmsClass?->name ?? '—', $item->teacher?->name ?? '—', $item->description ?: '—', $item->is_active ? 'Aktif' : 'Selesai']));
    }

    public function jobs(): View
    {
        return $this->listing('Lowongan', 'Informasi Penempatan', ['Posisi', 'Perusahaan', 'Lokasi', 'Tipe', 'Status'],
            Job::orderByDesc('created_at')->get()->map(fn ($item) => [$item->title, $item->company ?: '—', $item->location ?: '—', $item->employment_type ?: '—', $item->status]));
    }

    public function forums(): View
    {
        return $this->listing('Forum', 'Diskusi E-Learning', ['Topik', 'Penulis', 'Dibuat', 'Diperbarui'],
            ForumPost::with('author')->orderByDesc('created_at')->get()->map(fn ($item) => [$item->title ?: 'Tanpa judul', $item->author?->name ?? '—', $item->created_at ?: '—', $item->updated_at ?: '—']));
    }

    public function activities(): View
    {
        return $this->listing('Aktivitas', 'Aktivitas Akun Terbaru', ['Pengguna', 'Username', 'Role', 'Aktivitas', 'Waktu'],
            User::orderByDesc('created_at')->limit(50)->get()->map(fn ($item) => [$item->name, $item->username ?: '—', $item->role ?: '—', 'Akun terdaftar', $item->created_at ?: '—']));
    }

    public function settings(): View
    {
        return view('administration.settings');
    }

    private function listing(string $title, string $eyebrow, array $columns, $rows): View
    {
        return view('administration.listing', compact('title', 'eyebrow', 'columns', 'rows'));
    }
}
