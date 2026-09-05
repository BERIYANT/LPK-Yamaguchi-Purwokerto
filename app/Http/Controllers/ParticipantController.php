<?php

namespace App\Http\Controllers;

use App\Models\Payment;
use App\Models\StudentProfile;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rule;
use Illuminate\View\View;

class ParticipantController extends Controller
{
    public function index(Request $request): View
    {
        $year = max(2024, $request->integer('year', now()->year));

        $sortField = $request->get('sort', 'name');
        $sortDir = $request->get('direction', 'asc');

        $participants = User::with('studentProfile')->where('role', 'student')
            ->when($request->filled('q'), fn ($query) => $query->whereHas('studentProfile', fn ($profile) => $profile->where('nis', 'like', '%'.$request->q.'%')->orWhere('full_name', 'like', '%'.$request->q.'%')))
            ->when($request->filled('year'), fn ($query) => $query->whereHas('studentProfile', fn ($profile) => $profile->whereYear('enrollment_date', $year)))
            ->orderBy('full_name')->paginate(20)->withQueryString();

        // Apply sorting from the student profile relationship
        $participants->getCollection()->sortBy(function ($item) use ($sortField) {
            return match ($sortField) {
                'nis' => $item->studentProfile?->nis ?? '',
                'enrollment_date' => $item->studentProfile?->enrollment_date ?? '',
                'school_name' => $item->studentProfile?->school_name ?? '',
                'status' => $item->studentProfile?->status ?? 'aktif',
                default => $item->full_name ?? '',
            };
        }, SORT_REGULAR, $sortDir === 'desc');

        $years = StudentProfile::selectRaw('YEAR(enrollment_date) year')->whereYear('enrollment_date', '>=', 2024)->distinct()->orderByDesc('year')->pluck('year');

        return view('participants.index', compact('participants', 'years', 'year'));
    }

    public function create(): View
    {
        return view('participants.form');
    }

    public function store(Request $request): RedirectResponse
    {
        $data = $this->validated($request);
        $user = User::create(['username' => $data['nis'], 'full_name' => $data['full_name'], 'phone' => $data['phone'] ?? null, 'role' => 'student', 'password' => Hash::make(str()->random(24)), 'registration_completed' => 1]);
        $user->studentProfile()->create($data);

        return redirect()->route('participants.show', $data['nis'])->with('success', 'Data siswa berhasil disimpan.');
    }

    public function show(string $nis): View
    {
        $participant = User::with('studentProfile')->where('role', 'student')->whereHas('studentProfile', fn ($query) => $query->where('nis', $nis))->firstOrFail();
        $payments = Payment::where('user_id', $participant->id)->orderBy('payment_date')->get();

        return view('participants.show', compact('participant', 'payments'));
    }

    public function edit(string $nis): View
    {
        $participant = User::with('studentProfile')->where('role', 'student')->whereHas('studentProfile', fn ($query) => $query->where('nis', $nis))->firstOrFail();

        return view('participants.form', compact('participant'));
    }

    public function update(Request $request, string $nis): RedirectResponse
    {
        $participant = User::with('studentProfile')->where('role', 'student')->whereHas('studentProfile', fn ($query) => $query->where('nis', $nis))->firstOrFail();
        $profile = $participant->studentProfile;

        $data = $request->validate([
            'full_name' => ['required', 'string', 'max:255'],
            'gender' => ['nullable', Rule::in(['L', 'P'])], 'birth_place' => ['nullable', 'string', 'max:100'], 'birth_date' => ['nullable', 'date'],
            'school_name' => ['nullable', 'string', 'max:255'], 'nik' => ['nullable', 'string', 'max:30'], 'phone' => ['nullable', 'string', 'max:30'],
            'address' => ['nullable', 'string'], 'rt_rw' => ['nullable', 'string', 'max:20'], 'village' => ['nullable', 'string', 'max:100'],
            'district' => ['nullable', 'string', 'max:100'], 'city' => ['nullable', 'string', 'max:100'], 'province' => ['nullable', 'string', 'max:100'],
            'enrollment_date' => ['required', 'date'], 'graduation_date' => ['nullable', 'date'], 'departure_date' => ['nullable', 'date'],
            'job_sector' => ['nullable', 'string', 'max:100'], 'placement' => ['nullable', 'string', 'max:100'],
            'status' => ['required', Rule::in(['aktif', 'lulus', 'keluar', 'pending'])], 'notes' => ['nullable', 'string'],
        ]);

        $participant->update(['full_name' => $data['full_name'], 'phone' => $data['phone'] ?? null]);
        $profile->update($data);

        return redirect()->route('participants.show', $profile->nis)->with('success', 'Data siswa berhasil diperbarui.');
    }

    public function payments(Request $request): View
    {
        $year = max(2024, $request->integer('year', now()->year));
        $participant = null;
        $payments = collect();
        if ($request->filled('nis')) {
            $participant = User::with('studentProfile')->whereHas('studentProfile', fn ($query) => $query->where('nis', $request->nis))->first();
            $payments = $participant ? Payment::where('user_id', $participant->id)->orderBy('payment_date')->get() : collect();
        }
        $recap = Payment::with('user.studentProfile')->whereYear('payment_date', $year)->orderBy('payment_date')->get();

        return view('participants.payments', compact('participant', 'payments', 'recap', 'year'));
    }

    public function storePayment(Request $request): RedirectResponse
    {
        $data = $request->validate([
            'nis' => ['required', 'exists:student_profiles,nis'],
            'payment_type' => ['required', Rule::in(['registration', 'education_1', 'education_2', 'education_3', 'education_4', 'education_5', 'education_6', 'mcu', 'dormitory'])],
            'payment_date' => ['required', 'date'],
            'amount' => ['required', 'numeric', 'min:0'],
            'notes' => ['nullable', 'string', 'max:500'],
        ]);
        $user = User::whereHas('studentProfile', fn ($query) => $query->where('nis', $data['nis']))->firstOrFail();
        Payment::create(['user_id' => $user->id, 'payment_type' => $data['payment_type'], 'payment_date' => $data['payment_date'], 'amount' => $data['amount'], 'notes' => $data['notes'] ?? null, 'status' => 'verified']);

        return redirect()->route('participants.payments', ['nis' => $data['nis']])->with('success', 'Pembayaran berhasil disimpan.');
    }

    private function validated(Request $request): array
    {
        return $request->validate([
            'nis' => ['required', 'string', 'max:30', 'unique:student_profiles,nis'],
            'full_name' => ['required', 'string', 'max:255'],
            'gender' => ['nullable', Rule::in(['L', 'P'])], 'birth_place' => ['nullable', 'string', 'max:100'], 'birth_date' => ['nullable', 'date'],
            'school_name' => ['nullable', 'string', 'max:255'], 'nik' => ['nullable', 'string', 'max:30'], 'phone' => ['nullable', 'string', 'max:30'],
            'address' => ['nullable', 'string'], 'rt_rw' => ['nullable', 'string', 'max:20'], 'village' => ['nullable', 'string', 'max:100'],
            'district' => ['nullable', 'string', 'max:100'], 'city' => ['nullable', 'string', 'max:100'], 'province' => ['nullable', 'string', 'max:100'],
            'enrollment_date' => ['required', 'date'], 'graduation_date' => ['nullable', 'date'], 'departure_date' => ['nullable', 'date'],
            'job_sector' => ['nullable', 'string', 'max:100'], 'placement' => ['nullable', 'string', 'max:100'], 'status' => ['required', Rule::in(['aktif', 'lulus', 'keluar', 'pending'])], 'notes' => ['nullable', 'string'],
        ]);
    }
}
