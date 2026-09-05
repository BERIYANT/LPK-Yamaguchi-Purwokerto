<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('quiz_from_bank')]
class QuizFromBank extends LegacyModel
{
    public $timestamps = false;
}
