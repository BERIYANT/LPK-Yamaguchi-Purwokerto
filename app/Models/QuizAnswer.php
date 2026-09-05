<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('quiz_answers')]
class QuizAnswer extends LegacyModel
{
    public $timestamps = false;
}
