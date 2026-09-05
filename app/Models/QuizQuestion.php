<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('quiz_questions')]
class QuizQuestion extends LegacyModel
{
    public $timestamps = false;
}
