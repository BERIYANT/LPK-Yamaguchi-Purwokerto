<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('quiz_scores')]
class QuizScore extends LegacyModel
{
    public $timestamps = false;
    public function quiz(): BelongsTo { return $this->belongsTo(Quiz::class, 'quiz_id'); }
    public function student(): BelongsTo { return $this->belongsTo(User::class, 'student_id'); }
}
