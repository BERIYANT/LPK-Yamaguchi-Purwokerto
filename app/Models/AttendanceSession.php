<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('attendance_sessions')]
class AttendanceSession extends LegacyModel
{
    public $timestamps = false;

    public function lmsClass(): BelongsTo { return $this->belongsTo(LmsClass::class, 'class_id'); }
    public function teacher(): BelongsTo { return $this->belongsTo(User::class, 'teacher_id'); }
}
