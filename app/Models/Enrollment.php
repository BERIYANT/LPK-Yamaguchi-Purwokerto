<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('enrollments')]
class Enrollment extends LegacyModel
{
    public $timestamps = false;
    public function user(): BelongsTo { return $this->belongsTo(User::class, 'user_id'); }
    public function lmsClass(): BelongsTo { return $this->belongsTo(LmsClass::class, 'class_id'); }
}
