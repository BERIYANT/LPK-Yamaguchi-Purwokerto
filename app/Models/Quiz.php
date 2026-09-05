<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Table('quizzes')]
class Quiz extends LegacyModel
{
    public $timestamps = false;
    public function lmsClass(): BelongsTo { return $this->belongsTo(LmsClass::class, 'class_id'); }
    public function scores(): HasMany { return $this->hasMany(QuizScore::class, 'quiz_id'); }
}
