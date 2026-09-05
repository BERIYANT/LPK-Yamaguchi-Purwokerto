<?php

use App\Http\Controllers\Api\LmsController;
use Illuminate\Support\Facades\Route;

Route::middleware('auth:sanctum')->prefix('v1')->group(function () {
    Route::get('/participants', [LmsController::class, 'participants'])->middleware('role:admin,sensei');
    Route::get('/classes', [LmsController::class, 'classes']);
    Route::get('/tasks', [LmsController::class, 'tasks']);
});
