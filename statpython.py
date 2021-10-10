expectancy_at_birth_list = [76.84878, 81.40732, 77.57895, 74.16341, 68.84907,
                            73.88595, 75.26829, 76.26098, 80.57244, 65.46259,
                            67.5482, 55.02451, 76.2799, 82.29024, 69.80695,
                            81.40112, 82.19756, 74.22683, 80.12888, 45.55095]

no_of_elements = len(expectancy_at_birth_list)

sum_of_age_element = 0
for age in expectancy_at_birth_list:
    sum_of_age_element = sum_of_age_element + age

average_age = sum_of_age_element / no_of_elements

print("Average age: " + str(average_age))

expectancy_at_birth_list.sort()

num = no_of_elements // 2
mediana = (expectancy_at_birth_list[num] + expectancy_at_birth_list[num - 1]) / 2

print("Mediana age: " + str(mediana))

# domina = max(set(expectancy_at_birth_list), key=expectancy_at_birth_list.count)
# domina2 = expectancy_at_birth_list

# print(domina2)

suma = 0
for age in expectancy_at_birth_list:
    b = (age - average_age) ** 2
    suma += b
wariancja = suma / (len(expectancy_at_birth_list) - 1)

print("Wariancja: " + str(wariancja))

odchylenie_standardowe = wariancja ** (1 / 2)
print("Odchylenie standardowe: " + str(odchylenie_standardowe))

fertility_rate_list = [
    1.3, 1.95, 2.466, 1.6, 2.952,
    1.801, 1.34, 1.34, 1.63, 2.326,
    2.436, 6.563, 1.283, 1.43, 1.988,
    1.61, 1.921, 2.4, 1.495, 4.705]

no_of_elements = len(fertility_rate_list)

sum_of_fertility_element = 0
for rate in fertility_rate_list:
    sum_of_fertility_element = sum_of_fertility_element + rate

average_fertility = sum_of_fertility_element / no_of_elements

print("Average fertility: " + str(average_fertility))

suma = 0
for age in fertility_rate_list:
    c = (age - average_age) ** 2
    sum += c
wariancja_fertility = suma / (len(fertility_rate_list) - 1)

print("Wariancja fertility: " + str(wariancja_fertility))

odchylenie_standardowe_fertility = wariancja_fertility ** (1 / 2)
print("Odchylenie standardowe fertility: " + str(odchylenie_standardowe_fertility))

expectancy_at_birth_list2 = [76.84878, 81.40732, 77.57895, 74.16341, 68.84907,
                             73.88595, 75.26829, 76.26098, 80.57244, 65.46259,
                             67.5482, 55.02451, 76.2799, 82.29024, 69.80695,
                             81.40112, 82.19756, 74.22683, 80.12888, 45.55095]

suma = 0
ilosc = len(fertility_rate_list)
for i in range(0, ilosc):
    suma += (expectancy_at_birth_list2[i] - average_age) * (fertility_rate_list[i] - average_fertility)

result = suma / (ilosc - 1)

print("Kowariancja: " + str(result))

wspolczynnik_korelacji = result / (odchylenie_standardowe - odchylenie_standardowe_fertility)
print("Współczynnik korelacji: " + str(wspolczynnik_korelacji))

# 0,1<|r|≤0,3 – korelacja słaba
# Korelacja słaba - wskazuje na fakt, że dobrze się rozmnażać i poprawia to długość życia ale bez przesady
# i z umiarem ;)


# Na koniec postaraj się oszacować średnią oczekiwaną długość życia dla całej populacji przy poziomie ufności 95%.
# poziom istotności na poziomie 0,05
# Przyjmij, że odchylenie standardowe populacji wynosi 9,09.

x = poziom_istotnosci = 0.05
y = ochylenie_pop = 9.09
przedzial_ufnosci = average_age - x * (y / (no_of_elements ** (1 / 2))), \
                    average_age + x * (y / (no_of_elements ** (1 / 2)))

print("przedział ufności: " + str(przedzial_ufnosci))
print(average_age)

# Wartość ze znormalizowanego rozkładu normalnego odpowiadająca przyjętemu poziomowi istotności

w = average_age - (average_age - x * (y / (no_of_elements ** (1 / 2))))
print(w)

w1 = average_age - (average_age + x * (y / (no_of_elements ** (1 / 2))))
print(w1)

print("Wartość ze znormalizowanego rozkładu normalnego odpowiadająca poziomowi istotności 0,05 wynosi: " + str(w))
