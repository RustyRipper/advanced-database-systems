# advanced-database-systems

### Cel projektu

Celem projektu jest stworzenie kompleksowego systemu do zarządzania rezerwacjami miejsc parkingowych.
System pozwala użytkownikom na rezerwację miejsc na parkingach za pomocą aplikacji, jednocześnie umożliwiając
zarządzanie parkingami oraz opłatami przez administratorów i zarządców parkingów. System obsługuje procesy związane z
rezerwacjami, płatnościami oraz przypisywaniem miejsc parkingowych do użytkowników.

### Funkcje systemu

- Rejestracja i logowanie użytkowników: System umożliwia tworzenie kont użytkowników, w tym administratorów i zarządców
  parkingów, oraz zarządzanie danymi logowania.
- Zarządzanie miejscami parkingowymi: Zarządcy parkingu mogą tworzyć i edytować swoje parkingi, miejsca parkingowe oraz
  ustalać
  ceny rezerwacji.
- Rezerwacja miejsc parkingowych: Użytkownicy mogą przeglądać dostępne miejsca parkingowe w danym czasie i rezerwować
  je na określony czas.
- Obsługa płatności: System wspiera dokonywanie płatności za pomocą kart płatniczych, integrując się z zewnętrznymi
  systemami płatności (np. Stripe).
- Powiadomienia i raporty: Użytkownicy oraz zarządcy otrzymują powiadomienia o potwierdzeniach rezerwacji,
  płatnościach oraz dostępności miejsc parkingowych.

### Struktura danych

Baza danych systemu zawiera kluczowe tabele, które reprezentują główne elementy systemu:

- **Reservation** – Tabela przechowuje informacje o rezerwacjach, takie jak: identyfikator rezerwacji, powiązanie z
  użytkownikiem, miejsce parkingowe, czas rozpoczęcia i zakończenia rezerwacji, informacja o tym czy rezerwacja jest
  aktywna oraz koszty rezerwacji.

- **Parking** – Przechowuje dane dotyczące parkingów, takie jak: nazwa, lokalizacja,, godziny otwarcia,
  waluta, a także stawki za rezerwację miejsca parkingowego.

- **ParkingSpot** – Tabela przechowuje informacje o miejscach parkingowych, takie jak: identyfikator miejsca, powiązanie
  z
  parkingiem, informacja o tym czy miejsce jest aktywne oraz nazwa miejsca.

- **User** – Zawiera dane dotyczące użytkowników systemu, w tym: imię, nazwisko, adres e-mail, zaszyfrowane hasło, rola
  użytkownika (np. zwykły użytkownik, administrator, zarządca parkingu) oraz przypisane parkingi dla zarządców.

- **ClientCar** – Tabela przechowuje informacje o samochodach użytkowników, takie jak: czas dodania, numer
  rejestracyjny,
  marka, model,
  rok produkcji oraz powiązanie z użytkownikiem.

- **Payment** – Tabela odpowiedzialna za przechowywanie informacji o płatnościach, w tym: numer karty, kod CVC, data
  ważności
  karty oraz jednorazowy token płatniczy, który zapewnia bezpieczeństwo transakcji.

- **StripeCharge** – Przechowuje informacje o obciążeniach kart płatniczych wykonanych za pomocą systemu Stripe, takie
  jak:
  identyfikator obciążenia, kwota, waluta, status płatności oraz powiązanie z rezerwacją i płatnością.