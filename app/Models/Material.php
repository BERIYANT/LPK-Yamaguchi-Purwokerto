<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('materials')]
class Material extends LegacyModel
{
    public $timestamps = false;
    public function lmsClass(): BelongsTo { return $this->belongsTo(LmsClass::class, 'class_id'); }
    public function creator(): BelongsTo { return $this->belongsTo(User::class, 'created_by'); }
}
