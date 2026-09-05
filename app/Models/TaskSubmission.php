<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('task_submissions')]
class TaskSubmission extends LegacyModel
{
    public $timestamps = false;
    public function task(): BelongsTo { return $this->belongsTo(Task::class, 'task_id'); }
    public function student(): BelongsTo { return $this->belongsTo(User::class, 'student_id'); }
}
