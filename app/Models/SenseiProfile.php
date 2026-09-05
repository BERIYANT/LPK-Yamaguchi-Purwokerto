<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('sensei_profiles')]
class SenseiProfile extends LegacyModel
{
    public function user(): BelongsTo { return $this->belongsTo(User::class, 'user_id'); }
}
