<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('student_profiles')]
class StudentProfile extends LegacyModel
{
    public function user(): BelongsTo { return $this->belongsTo(User::class, 'user_id'); }
}
