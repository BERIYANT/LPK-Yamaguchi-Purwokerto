<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Hidden;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

#[Table('users')]
#[Hidden(['password'])]
class User extends Authenticatable
{
    use Notifiable;

    public $timestamps = false;

    protected $primaryKey = 'id';

    protected $guarded = [];

    public function getNameAttribute(): string
    {
        return $this->full_name ?: ($this->username ?: 'Pengguna');
    }

    public function studentProfile(): HasOne
    {
        return $this->hasOne(StudentProfile::class, 'user_id');
    }

    public function senseiProfile(): HasOne
    {
        return $this->hasOne(SenseiProfile::class, 'user_id');
    }

    public function enrollments(): HasMany
    {
        return $this->hasMany(Enrollment::class, 'user_id');
    }

    public function payments(): HasMany
    {
        return $this->hasMany(Payment::class, 'user_id');
    }
}
