<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Table('tasks')]
class Task extends LegacyModel
{
    public $timestamps = false;
    public function lmsClass(): BelongsTo { return $this->belongsTo(LmsClass::class, 'class_id'); }
    public function submissions(): HasMany { return $this->hasMany(TaskSubmission::class, 'task_id'); }
}
