<?php

namespace App\Http\Controllers;

use App\Models\TaskSubmission;
use Illuminate\View\View;

class GradeController extends Controller
{
    public function index(): View
    {
        return view('grades.index', ['submissions' => TaskSubmission::with(['task', 'student'])->latest('submitted_at')->paginate(20)]);
    }
}
