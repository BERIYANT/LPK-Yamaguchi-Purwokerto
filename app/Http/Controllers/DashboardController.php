<?php

namespace App\Http\Controllers;

use App\Models\AttendanceRecord;
use App\Models\AttendanceSession;
use App\Models\LmsClass;
use App\Models\Material;
use App\Models\Quiz;
use App\Models\Task;
use App\Models\TaskSubmission;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\View\View;

class DashboardController extends Controller
{
    public function __invoke(Request $request): View
    {
        $metrics = [
            'participants' => User::where('role', 'student')->count(),
            'sensei' => User::where('role', 'sensei')->count(),
            'classes' => LmsClass::count(),
            'materials' => Material::count(),
            'tasks' => Task::count(),
            'pendingGrades' => TaskSubmission::whereNull('grade')->whereNull('score')->count(),
        ];

        $attendanceTotal = AttendanceRecord::count();
        $attendance = [
            ['label' => 'Hadir', 'value' => $attendanceTotal, 'percentage' => $attendanceTotal ? 100 : 0, 'color' => '#a91820'],
            ['label' => 'Tidak hadir', 'value' => 0, 'percentage' => 0, 'color' => '#d62828'],
            ['label' => 'Terlambat', 'value' => 0, 'percentage' => 0, 'color' => '#e13b32'],
            ['label' => 'Izin', 'value' => 0, 'percentage' => 0, 'color' => '#ef6a61'],
        ];

        $monthlyStudents = collect(range(1, 12))->map(function (int $month) {
            return User::where('role', 'student')
                ->whereYear('created_at', now()->year)
                ->whereMonth('created_at', $month)
                ->count();
        });
        $monthlyAcademic = collect(range(1, 12))->map(function (int $month) {
            return Task::whereYear('created_at', now()->year)->whereMonth('created_at', $month)->count()
                + Quiz::whereYear('created_at', now()->year)->whereMonth('created_at', $month)->count();
        });
        $chartMaximum = max(1, $monthlyStudents->max(), $monthlyAcademic->max());

        $calendarDate = Carbon::createSafe(
            $request->integer('year', now()->year),
            $request->integer('month', now()->month),
            1,
        ) ?? now()->startOfMonth();
        $calendarDays = collect(range(0, $calendarDate->dayOfWeek - 1))->map(fn () => null)
            ->concat(range(1, $calendarDate->daysInMonth));

        return view('dashboard', [
            'metrics' => $metrics,
            'attendance' => $attendance,
            'attendanceSessions' => AttendanceSession::count(),
            'monthlyStudents' => $monthlyStudents,
            'monthlyAcademic' => $monthlyAcademic,
            'chartMaximum' => $chartMaximum,
            'calendarDate' => $calendarDate,
            'calendarDays' => $calendarDays,
            'previousMonth' => $calendarDate->copy()->subMonth(),
            'nextMonth' => $calendarDate->copy()->addMonth(),
            'recentParticipants' => User::where('role', 'student')->latest('id')->limit(6)->get(),
            'upcomingTasks' => Task::with('lmsClass')->whereNotNull('due_date')->orderBy('due_date')->limit(5)->get(),
            'recentQuizzes' => Quiz::with('lmsClass')->latest('id')->limit(5)->get(),
        ]);
    }
}
