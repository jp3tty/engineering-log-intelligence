-- Active users and their last activity
SELECT 
    id,
    username,
    email,
    role,
    is_active,
    last_login,
    EXTRACT(DAY FROM NOW() - last_login) as days_since_login,
    created_at,
    EXTRACT(DAY FROM NOW() - created_at) as account_age_days
FROM users
ORDER BY last_login DESC NULLS LAST;