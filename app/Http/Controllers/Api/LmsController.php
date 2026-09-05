<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\LmsClass;
use App\Models\Task;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class LmsController extends Controller
{
    public function participants(Request $request): JsonResponse { return response()->json(User::where('role', 'student')->paginate($request->integer('per_page', 20))); }
    public function classes(): JsonResponse { return response()->json(LmsClass::withCount('enrollments')->get()); }
    public function tasks(): JsonResponse { return response()->json(Task::with('lmsClass')->latest('id')->paginate(20)); }
}
