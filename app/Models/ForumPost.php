<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('forum_posts')]
class ForumPost extends LegacyModel
{
    public function author(): BelongsTo { return $this->belongsTo(User::class, 'user_id'); }
}
