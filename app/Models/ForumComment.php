<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('forum_comments')]
class ForumComment extends LegacyModel
{
    public $timestamps = false;
}
