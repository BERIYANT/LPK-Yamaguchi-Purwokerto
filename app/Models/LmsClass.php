<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Table('classes')]
class LmsClass extends LegacyModel
{
    public $timestamps = false;

    public function teacher(): BelongsTo { return $this->belongsTo(User::class, 'teacher_id'); }
    public function enrollments(): HasMany { return $this->hasMany(Enrollment::class, 'class_id'); }
    public function materials(): HasMany { return $this->hasMany(Material::class, 'class_id'); }
    public function tasks(): HasMany { return $this->hasMany(Task::class, 'class_id'); }
    public function quizzes(): HasMany { return $this->hasMany(Quiz::class, 'class_id'); }
}
