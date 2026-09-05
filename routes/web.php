<?php

use App\Http\Controllers\ClassController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\GradeController;
use App\Http\Controllers\ParticipantController;
use App\Http\Controllers\AdministrationController;
use Illuminate\Support\Facades\Route;

Route::view('/', 'index')->name('home');

Route::middleware('auth')->group(function () {
    Route::get('/dashboard', DashboardController::class)->name('dashboard');
    Route::get('/kelas', [ClassController::class, 'index'])->name('classes.index');

    Route::middleware('role:admin,sensei')->group(function () {
        Route::get('/peserta', [ParticipantController::class, 'index'])->name('participants.index');
        Route::get('/peserta/tambah', [ParticipantController::class, 'create'])->name('participants.create');
        Route::post('/peserta', [ParticipantController::class, 'store'])->name('participants.store');
        Route::get('/peserta/pembayaran', [ParticipantController::class, 'payments'])->name('participants.payments');
        Route::post('/peserta/pembayaran', [ParticipantController::class, 'storePayment'])->name('participants.payments.store');
        Route::get('/peserta/{nis}', [ParticipantController::class, 'show'])->name('participants.show');
        Route::get('/penilaian', [GradeController::class, 'index'])->name('grades.index');
    });

    Route::middleware('role:admin')->prefix('admin')->group(function () {
        Route::get('/sensei', [AdministrationController::class, 'sensei'])->name('admin.sensei');
        Route::post('/sensei', [AdministrationController::class, 'storeSensei'])->name('admin.sensei.store');
        Route::get('/jadwal-sensei', [AdministrationController::class, 'schedules'])->name('admin.schedules');
        Route::get('/akun', [AdministrationController::class, 'accounts'])->name('admin.accounts');
        Route::get('/aktivitas', [AdministrationController::class, 'activities'])->name('admin.activities');
        Route::get('/absensi', [AdministrationController::class, 'attendance'])->name('admin.attendance');
        Route::get('/lowongan', [AdministrationController::class, 'jobs'])->name('admin.jobs');
        Route::get('/forum', [AdministrationController::class, 'forums'])->name('admin.forums');
        Route::get('/pengaturan', [AdministrationController::class, 'settings'])->name('admin.settings');
    });

});

require __DIR__.'/auth.php';
