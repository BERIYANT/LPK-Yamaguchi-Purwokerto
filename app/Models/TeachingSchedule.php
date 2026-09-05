<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('teaching_schedules')]
class TeachingSchedule extends LegacyModel
{
    public $timestamps = false;

    public function sensei(): BelongsTo
    {
        return $this->belongsTo(SenseiProfile::class, 'sensei_id');
    }
}
