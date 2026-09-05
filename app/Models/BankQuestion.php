<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('bank_questions')]
class BankQuestion extends LegacyModel
{
    public $timestamps = false;
}
