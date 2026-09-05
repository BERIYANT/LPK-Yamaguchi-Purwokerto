<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('assignment_from_bank')]
class AssignmentFromBank extends LegacyModel
{
    public $timestamps = false;
}
