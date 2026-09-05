<?php

namespace App\Http\Controllers;

use App\Models\LmsClass;
use Illuminate\View\View;

class ClassController extends Controller
{
    public function index(): View
    {
        return view('classes.index', ['classes' => LmsClass::with('teacher')->withCount(['enrollments', 'materials', 'tasks'])->orderBy('name')->get()]);
    }
}
